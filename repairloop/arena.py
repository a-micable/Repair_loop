"""Head-to-head model arena on the same task."""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable

from .config import load_settings
from .pipeline import run_pipeline
from .session import AgentResult, run_session
from .tasks import Task, load_task

ProgressCb = Callable[[dict[str, Any]], None]


@dataclass
class ArenaResult:
    task_id: str
    left_model: str
    right_model: str
    left: dict[str, Any]
    right: dict[str, Any]
    winner: str
    reason: str


def _pack(result: AgentResult) -> dict[str, Any]:
    return {
        "success": result.success,
        "iterations": result.iterations,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "est_cost_usd": result.est_cost_usd,
        "seconds": None,
        "final_code": result.final_code,
        "error": result.error,
        "transcript_path": result.transcript_path,
    }


def run_arena(
    task: Task | str,
    *,
    left_model: str,
    right_model: str,
    pipeline: bool = True,
    max_iters: int = 4,
    on_progress: ProgressCb | None = None,
) -> ArenaResult:
    if isinstance(task, str):
        task = load_task(task)
    settings = load_settings()
    original = settings.model

    def _one(model: str, label: str) -> dict[str, Any]:
        os.environ["NEBIUS_MODEL"] = model
        if on_progress:
            on_progress({"event": "arena", "side": label, "model": model, "phase": "start"})
        t0 = time.time()
        if pipeline:
            result = run_pipeline(task, max_iters=max_iters, on_progress=on_progress)
        else:
            result = run_session(task, max_iters=max_iters, on_progress=on_progress)
        packed = _pack(result)
        packed["seconds"] = round(time.time() - t0, 2)
        packed["model"] = model
        if on_progress:
            on_progress(
                {
                    "event": "arena",
                    "side": label,
                    "model": model,
                    "phase": "done",
                    "success": result.success,
                }
            )
        return packed

    try:
        left = _one(left_model, "left")
        right = _one(right_model, "right")
    finally:
        os.environ["NEBIUS_MODEL"] = original

    winner, reason = _judge(left, right)
    return ArenaResult(
        task_id=task.id,
        left_model=left_model,
        right_model=right_model,
        left=left,
        right=right,
        winner=winner,
        reason=reason,
    )


def _judge(left: dict[str, Any], right: dict[str, Any]) -> tuple[str, str]:
    if left["success"] and not right["success"]:
        return "left", "only left passed grader"
    if right["success"] and not left["success"]:
        return "right", "only right passed grader"
    if left["success"] and right["success"]:
        if left["iterations"] != right["iterations"]:
            w = "left" if left["iterations"] < right["iterations"] else "right"
            return w, "fewer repair iterations"
        if left["est_cost_usd"] != right["est_cost_usd"]:
            w = "left" if left["est_cost_usd"] < right["est_cost_usd"] else "right"
            return w, "lower estimated cost"
        return "tie", "both passed with similar cost/iters"
    return "tie", "neither passed"
