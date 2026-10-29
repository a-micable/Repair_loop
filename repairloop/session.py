from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .config import estimate_cost_usd, load_settings
from .llm import NebiusClient
from .prompts import SYSTEM, extract_python, user_task
from .sandbox import Workspace
from .tasks import Task, load_task
from .tools import ToolRouter, openai_tool_schemas
from .transcript import Transcript

ProgressCb = Callable[[dict[str, Any]], None]


@dataclass
class AgentResult:
    success: bool
    task_id: str
    model: str
    final_code: str
    iterations: int
    tool_events: list[dict[str, Any]] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    est_cost_usd: float = 0.0
    transcript_path: str = ""
    error: str = ""


def run_session(
    task: Task | str,
    *,
    max_iters: int | None = None,
    on_progress: ProgressCb | None = None,
    keep_workspace: Path | None = None,
) -> AgentResult:
    settings = load_settings()
    if isinstance(task, str):
        task = load_task(task)

    budget = max_iters or settings.max_iters
    client = NebiusClient(settings)
    ws = Workspace(keep_workspace)
    tools = ToolRouter(ws, test_source=task.test_source, settings=settings)
    allow_tavily = settings.has_tavily
    schemas = openai_tool_schemas(allow_tavily)

    transcript = Transcript(
        Path(settings.runs_dir), task_id=task.id, model=client.model
    )
    transcript.event("task", title=task.title, difficulty=task.difficulty)

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": user_task(
                task.prompt, task.public_tests_hint, tavily_on=allow_tavily
            ),
        },
    ]

    final_code = ""
    iterations = 0

    try:
        for i in range(1, budget + 1):
            iterations = i
            if on_progress:
                on_progress({"event": "thinking", "iteration": i, "model": client.model})
            transcript.event("thinking", iteration=i)

            try:
                reply = client.chat(messages, tools=schemas)
            except Exception:
                # some models reject tools — fall back to plain chat + fence parse
                reply = client.chat(messages, tools=None)
                if reply["content"] and not reply["tool_calls"]:
                    code = extract_python(reply["content"])
                    if code.strip():
                        tools.dispatch(
                            "write_file",
                            {"path": "solution.py", "content": code},
                        )
                        grade = tools.dispatch("run_tests", {})
                        if on_progress:
                            on_progress(
                                {
                                    "event": "test",
                                    "iteration": i,
                                    "ok": tools.last_grader_ok,
                                    "detail": grade,
                                }
                            )
                        transcript.event(
                            "fallback_grade",
                            iteration=i,
                            ok=tools.last_grader_ok,
                            detail=grade[:2000],
                        )
                        if tools.last_grader_ok:
                            final_code = _safe_read(ws)
                            break
                        messages.append(
                            {"role": "assistant", "content": reply["content"]}
                        )
                        messages.append(
                            {
                                "role": "user",
                                "content": (
                                    "Tests failed. Fix solution.py.\n\n" + grade
                                ),
                            }
                        )
                        continue
                raise

            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": reply["content"] or None,
            }
            if reply["tool_calls"]:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc["arguments"],
                        },
                    }
                    for tc in reply["tool_calls"]
                ]
            messages.append(assistant_msg)

            if not reply["tool_calls"]:
                # model dumped code in plain text — accept it and grade
                code = extract_python(reply["content"])
                if code.strip():
                    tools.dispatch(
                        "write_file", {"path": "solution.py", "content": code}
                    )
                    grade = tools.dispatch("run_tests", {})
                    if on_progress:
                        on_progress(
                            {
                                "event": "test",
                                "iteration": i,
                                "ok": tools.last_grader_ok,
                                "detail": grade,
                            }
                        )
                    if tools.last_grader_ok:
                        final_code = code
                        break
                    messages.append(
                        {
                            "role": "user",
                            "content": "Tests failed. Use tools to fix.\n\n" + grade,
                        }
                    )
                continue

            for tc in reply["tool_calls"]:
                result = tools.dispatch(tc["name"], tc["arguments"])
                if on_progress:
                    on_progress(
                        {
                            "event": "tool",
                            "iteration": i,
                            "name": tc["name"],
                            "result": result[:1500],
                            "ok": tools.last_grader_ok
                            if tc["name"] == "run_tests"
                            else None,
                        }
                    )
                transcript.event(
                    "tool",
                    iteration=i,
                    name=tc["name"],
                    result=result[:3000],
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result[:8000],
                    }
                )

            final_code = _safe_read(ws)
            if tools.last_grader_ok:
                break

        success = tools.last_grader_ok
        cost = estimate_cost_usd(
            client.model,
            client.meter.prompt_tokens,
            client.meter.completion_tokens,
        )
        path = transcript.finish(
            success=success,
            iterations=iterations,
            prompt_tokens=client.meter.prompt_tokens,
            completion_tokens=client.meter.completion_tokens,
            est_cost_usd=cost,
        )
        return AgentResult(
            success=success,
            task_id=task.id,
            model=client.model,
            final_code=final_code,
            iterations=iterations,
            tool_events=tools.history,
            prompt_tokens=client.meter.prompt_tokens,
            completion_tokens=client.meter.completion_tokens,
            est_cost_usd=cost,
            transcript_path=str(path),
        )
    except Exception as exc:  # noqa: BLE001
        transcript.finish(success=False, error=str(exc))
        return AgentResult(
            success=False,
            task_id=task.id,
            model=client.model,
            final_code=_safe_read(ws),
            iterations=iterations,
            tool_events=tools.history,
            prompt_tokens=client.meter.prompt_tokens,
            completion_tokens=client.meter.completion_tokens,
            est_cost_usd=estimate_cost_usd(
                client.model,
                client.meter.prompt_tokens,
                client.meter.completion_tokens,
            ),
            transcript_path=str(transcript.path),
            error=str(exc),
        )
    finally:
        if keep_workspace is None:
            ws.cleanup()


def _safe_read(ws: Workspace) -> str:
    try:
        return ws.read("solution.py")
    except Exception:
        return ""
