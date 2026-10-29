"""
LabForge multi-stage pipeline:

  research (optional Tavily + skills) → code/repair loop → critic pass

The critic does not write code; it only returns structured feedback that
gets fed into another coding round when the grader still fails.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict
from typing import Any, Callable

from .config import estimate_cost_usd, load_settings
from .distill import distill_success
from .llm import NebiusClient
from .session import AgentResult, run_session
from .skills import format_skills, retrieve
from .store import Store
from .tasks import Task, load_task
from .tavily import format_for_model, search

ProgressCb = Callable[[dict[str, Any]], None]


RESEARCH_SYS = """You are a lab research assistant.
Given a STEM coding task, list the formulas / pitfalls the coder must get right.
If web_search results are provided, cite only what is needed.
Return compact markdown bullets. No code."""


CRITIC_SYS = """You are a strict code reviewer for scientific Python.
You see the task, the failing grader output, and the current solution.
Explain the likely bug in under 12 lines. Do not rewrite the whole file.
If the failure is clear, propose a concrete fix hint."""


def _research_brief(
    client: NebiusClient,
    task: Task,
    *,
    use_tavily: bool,
    on_progress: ProgressCb | None,
) -> str:
    settings = load_settings()
    skills = retrieve(task.prompt + " " + " ".join(task.tags or []), k=3)
    skill_txt = format_skills(skills)

    web_txt = "(tavily off)"
    if use_tavily and settings.has_tavily:
        # one targeted query — keep credits sane
        q = f"{task.title} formula python numerical method"
        if on_progress:
            on_progress({"event": "research", "phase": "tavily", "query": q})
        web_txt = format_for_model(search(q, settings.tavily_api_key))

    if on_progress:
        on_progress(
            {
                "event": "research",
                "phase": "skills",
                "skills": [s.id for s in skills],
            }
        )

    msg = client.chat(
        [
            {"role": "system", "content": RESEARCH_SYS},
            {
                "role": "user",
                "content": (
                    f"# Task\n{task.prompt}\n\n"
                    f"# Skill pack hits\n{skill_txt}\n\n"
                    f"# Web search\n{web_txt}\n"
                ),
            },
        ],
        temperature=0.2,
        max_tokens=900,
    )
    return msg["content"]


def _critic(
    client: NebiusClient,
    task: Task,
    code: str,
    grade_detail: str,
) -> str:
    msg = client.chat(
        [
            {"role": "system", "content": CRITIC_SYS},
            {
                "role": "user",
                "content": (
                    f"# Task\n{task.prompt}\n\n"
                    f"# solution.py\n```python\n{code}\n```\n\n"
                    f"# Grader\n{grade_detail}\n"
                ),
            },
        ],
        temperature=0.1,
        max_tokens=700,
    )
    return msg["content"]


def run_pipeline(
    task: Task | str,
    *,
    max_iters: int | None = None,
    use_tavily: bool | None = None,
    use_critic: bool = True,
    on_progress: ProgressCb | None = None,
) -> AgentResult:
    settings = load_settings()
    if isinstance(task, str):
        task = load_task(task)

    tavily_on = settings.has_tavily if use_tavily is None else (use_tavily and settings.has_tavily)
    client = NebiusClient(settings)

    if on_progress:
        on_progress({"event": "pipeline", "stage": "research"})

    brief = _research_brief(client, task, use_tavily=tavily_on, on_progress=on_progress)

    # inject research into a shallow copy of the task prompt
    enriched = Task(
        id=task.id,
        title=task.title,
        difficulty=task.difficulty,
        prompt=(
            task.prompt
            + "\n\n# Research brief (from LabForge researcher)\n"
            + brief
        ),
        public_tests_hint=task.public_tests_hint,
        test_source=task.test_source,
        track_fit=task.track_fit,
        tags=task.tags,
        raw=task.raw,
    )

    if on_progress:
        on_progress({"event": "pipeline", "stage": "code", "brief_chars": len(brief)})

    result = run_session(enriched, max_iters=max_iters, on_progress=on_progress)

    # merge research tokens already on client — session has its own client.
    # We approximate by summing after the fact in store meta.
    research_tokens = client.meter.total_tokens

    if (not result.success) and use_critic and result.final_code:
        if on_progress:
            on_progress({"event": "pipeline", "stage": "critic"})
        # pull last grader fail from tool events
        grade_detail = ""
        for ev in reversed(result.tool_events):
            if ev.get("tool") == "run_tests":
                grade_detail = str(ev.get("result") or "")
                break
        critique = _critic(client, task, result.final_code, grade_detail or "(no detail)")
        if on_progress:
            on_progress({"event": "critic", "text": critique[:1000]})

        # one more coding burst with critic notes baked in
        enriched2 = Task(
            id=task.id,
            title=task.title,
            difficulty=task.difficulty,
            prompt=(
                task.prompt
                + "\n\n# Research brief\n"
                + brief
                + "\n\n# Critic notes on previous failing attempt\n"
                + critique
                + "\n\n# Previous solution.py\n```python\n"
                + result.final_code
                + "\n```\n"
            ),
            public_tests_hint=task.public_tests_hint,
            test_source=task.test_source,
            track_fit=task.track_fit,
            tags=task.tags,
            raw=task.raw,
        )
        result2 = run_session(
            enriched2, max_iters=max(2, (max_iters or 3) // 2), on_progress=on_progress
        )
        # prefer the successful one
        if result2.success or (
            result2.prompt_tokens + result2.completion_tokens
            >= result.prompt_tokens + result.completion_tokens
        ):
            # combine token counts
            result2.prompt_tokens += result.prompt_tokens + client.meter.prompt_tokens
            result2.completion_tokens += (
                result.completion_tokens + client.meter.completion_tokens
            )
            result2.iterations += result.iterations
            result = result2
        else:
            result.prompt_tokens += client.meter.prompt_tokens
            result.completion_tokens += client.meter.completion_tokens
    else:
        result.prompt_tokens += client.meter.prompt_tokens
        result.completion_tokens += client.meter.completion_tokens

    result.est_cost_usd = estimate_cost_usd(
        result.model, result.prompt_tokens, result.completion_tokens
    )

    # persist + optional skill distillation on PASS
    distilled = None
    if result.success and result.final_code.strip():
        try:
            distilled = str(
                distill_success(
                    task_id=task.id, code=result.final_code, model=result.model
                )
            )
        except Exception:
            distilled = None

    store = Store()
    store.record_run(
        {
            "id": uuid.uuid4().hex,
            "task_id": task.id,
            "model": result.model,
            "success": result.success,
            "iterations": result.iterations,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "est_cost_usd": result.est_cost_usd,
            "pipeline": "research-code-critic" if use_critic else "research-code",
            "transcript_path": result.transcript_path,
            "created_at": time.time(),
            "meta": {
                "tavily": tavily_on,
                "research_tokens": research_tokens,
                "brief_preview": brief[:400],
                "distilled_skill": distilled,
            },
        }
    )

    if on_progress:
        on_progress(
            {
                "event": "pipeline",
                "stage": "done",
                "success": result.success,
            }
        )
    return result
