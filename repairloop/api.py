"""HTTP API for LabForge — run pipelines, inspect leaderboard, list tasks."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fastapi.responses import PlainTextResponse

from . import __version__
from . import metrics
from .config import load_settings
from .pipeline import run_pipeline
from .session import run_session
from .skills import load_skills, retrieve
from .store import Store
from .tasks import list_tasks, load_task

app = FastAPI(
    title="LabForge API",
    description="STEM coding agents on Nebius Token Factory / NVIDIA Nemotron",
    version=__version__,
)


class RunRequest(BaseModel):
    task_id: str
    pipeline: bool = True
    max_iters: int | None = None
    use_tavily: bool | None = None
    use_critic: bool = True


@app.get("/health")
def health() -> dict[str, Any]:
    s = load_settings()
    return {
        "ok": True,
        "version": __version__,
        "nebius": s.has_nebius,
        "tavily": s.has_tavily,
        "model": s.model,
        "tasks": len(list_tasks()),
        "metrics": metrics.snapshot(),
    }


@app.get("/metrics")
def prometheus_metrics() -> PlainTextResponse:
    return PlainTextResponse(metrics.render_prometheus(), media_type="text/plain")


@app.get("/tasks")
def tasks() -> list[dict[str, Any]]:
    return [
        {
            "id": t.id,
            "title": t.title,
            "difficulty": t.difficulty,
            "tags": t.tags or [],
        }
        for t in list_tasks()
    ]


@app.get("/skills")
def skills(q: str | None = None) -> list[dict[str, Any]]:
    items = retrieve(q, k=8) if q else load_skills()
    return [
        {"id": s.id, "title": s.title, "tags": s.tags, "score": getattr(s, "score", 0)}
        for s in items
    ]


@app.get("/leaderboard")
def leaderboard() -> dict[str, Any]:
    store = Store()
    return {"models": store.leaderboard(), "tasks": store.task_stats()}


@app.get("/runs")
def runs(limit: int = 40) -> list[dict[str, Any]]:
    return Store().recent(limit=limit)


@app.post("/run")
def run(req: RunRequest) -> dict[str, Any]:
    settings = load_settings()
    if not settings.has_nebius:
        raise HTTPException(400, "NEBIUS_API_KEY not configured")
    try:
        task = load_task(req.task_id)
    except FileNotFoundError as exc:
        raise HTTPException(404, str(exc)) from exc

    if req.pipeline:
        result = run_pipeline(
            task,
            max_iters=req.max_iters,
            use_tavily=req.use_tavily,
            use_critic=req.use_critic,
        )
    else:
        result = run_session(task, max_iters=req.max_iters)

    return {
        "success": result.success,
        "task_id": result.task_id,
        "model": result.model,
        "iterations": result.iterations,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "est_cost_usd": result.est_cost_usd,
        "transcript_path": result.transcript_path,
        "error": result.error,
        "final_code": result.final_code,
    }


def main() -> None:
    import uvicorn

    uvicorn.run("repairloop.api:app", host="0.0.0.0", port=8080, reload=False)


if __name__ == "__main__":
    main()
