"""Multi-model / multi-task bakeoff with markdown report."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from .config import load_settings
from .pipeline import run_pipeline
from .session import run_session
from .tasks import list_tasks


def run_bakeoff(
    *,
    models: list[str],
    task_ids: list[str] | None,
    pipeline: bool,
    max_iters: int,
) -> dict[str, Any]:
    settings = load_settings()
    tasks = list_tasks()
    if task_ids:
        wanted = set(task_ids)
        tasks = [t for t in tasks if t.id in wanted]

    rows: list[dict[str, Any]] = []
    for model in models:
        os.environ["NEBIUS_MODEL"] = model
        for task in tasks:
            t0 = time.time()
            if pipeline:
                result = run_pipeline(task, max_iters=max_iters)
            else:
                result = run_session(task, max_iters=max_iters)
            rows.append(
                {
                    "model": model,
                    "task": task.id,
                    "difficulty": task.difficulty,
                    "success": result.success,
                    "iters": result.iterations,
                    "prompt_tokens": result.prompt_tokens,
                    "completion_tokens": result.completion_tokens,
                    "est_cost_usd": result.est_cost_usd,
                    "seconds": round(time.time() - t0, 2),
                    "error": result.error,
                }
            )
    os.environ["NEBIUS_MODEL"] = settings.model
    return {
        "created_at": time.time(),
        "pipeline": pipeline,
        "rows": rows,
        "summary": _summarize(rows),
    }


def _summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by.setdefault(r["model"], []).append(r)
    out = []
    for model, rs in by.items():
        n = len(rs)
        passes = sum(1 for r in rs if r["success"])
        out.append(
            {
                "model": model,
                "n": n,
                "passes": passes,
                "pass_rate": passes / n if n else 0.0,
                "avg_iters": sum(r["iters"] for r in rs) / n if n else 0.0,
                "tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rs),
                "cost_usd": sum(r["est_cost_usd"] for r in rs),
            }
        )
    out.sort(key=lambda x: (-x["pass_rate"], x["avg_iters"]))
    return out


def to_markdown(report: dict[str, Any]) -> str:
    lines = ["# LabForge bakeoff", "", "## Summary", ""]
    lines.append("| model | pass_rate | n | avg_iters | tokens | cost_usd |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for s in report["summary"]:
        lines.append(
            f"| `{s['model']}` | {s['pass_rate']:.2%} | {s['n']} | "
            f"{s['avg_iters']:.1f} | {s['tokens']} | {s['cost_usd']:.4f} |"
        )
    lines.extend(["", "## Per-task", ""])
    lines.append("| model | task | ok | iters | sec | cost |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for r in report["rows"]:
        lines.append(
            f"| `{r['model']}` | {r['task']} | {int(r['success'])} | "
            f"{r['iters']} | {r['seconds']} | {r['est_cost_usd']:.5f} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="labforge-bench")
    p.add_argument("--model", action="append", dest="models", default=[])
    p.add_argument("--task", action="append", default=[])
    p.add_argument("--pipeline", action="store_true")
    p.add_argument("--iters", type=int, default=4)
    p.add_argument("--out", default="runs/bakeoff.json")
    args = p.parse_args(argv)

    models = args.models or [load_settings().model]
    report = run_bakeoff(
        models=models,
        task_ids=args.task or None,
        pipeline=args.pipeline,
        max_iters=args.iters,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md = out.with_suffix(".md")
    md.write_text(to_markdown(report), encoding="utf-8")
    print(to_markdown(report))
    print("wrote", out, md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
