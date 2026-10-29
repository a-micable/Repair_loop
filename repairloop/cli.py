from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .config import load_settings
from .pipeline import run_pipeline
from .session import run_session
from .tasks import list_tasks, load_task


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="repairloop",
        description="LabForge — STEM coding agents on Nebius / Nemotron",
    )
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="run agent on one task")
    run_p.add_argument("task")
    run_p.add_argument("--iters", type=int, default=None)
    run_p.add_argument(
        "--pipeline",
        action="store_true",
        help="research → code → critic (default for prize demos)",
    )
    run_p.add_argument("--no-tavily", action="store_true")
    run_p.add_argument("--no-critic", action="store_true")

    sub.add_parser("tasks", help="list tasks")

    eval_p = sub.add_parser("eval", help="oracle check / agent suite")
    eval_p.add_argument("--oracles-only", action="store_true")
    eval_p.add_argument("--agent", action="store_true")
    eval_p.add_argument("--task", action="append", default=[])
    eval_p.add_argument("--iters", type=int, default=5)

    args = p.parse_args(argv)

    if args.cmd == "tasks":
        for t in list_tasks():
            tags = ",".join(t.tags or [])
            print(f"{t.id:24} {t.difficulty:8} {t.title}  [{tags}]")
        return 0

    if args.cmd == "eval":
        from .eval import main as eval_main

        argv2 = []
        if args.oracles_only:
            argv2.append("--oracles-only")
        if args.agent:
            argv2.append("--agent")
        for t in args.task:
            argv2.extend(["--task", t])
        argv2.extend(["--iters", str(args.iters)])
        return eval_main(argv2)

    if args.cmd == "run":
        settings = load_settings()
        print("model:", settings.model)
        print("tavily:", "on" if settings.has_tavily else "off")
        task = load_task(args.task)

        def on_progress(evt: dict) -> None:
            e = evt.get("event")
            if e in {"pipeline", "research", "critic", "thinking", "tool", "test"}:
                print(e, {k: v for k, v in evt.items() if k != "event"})

        if args.pipeline:
            result = run_pipeline(
                task,
                max_iters=args.iters,
                use_tavily=not args.no_tavily,
                use_critic=not args.no_critic,
                on_progress=on_progress,
            )
        else:
            result = run_session(task, max_iters=args.iters, on_progress=on_progress)

        print(
            json.dumps(
                {
                    "success": result.success,
                    "iters": result.iterations,
                    "tokens": result.prompt_tokens + result.completion_tokens,
                    "est_cost_usd": result.est_cost_usd,
                    "transcript": result.transcript_path,
                    "error": result.error,
                },
                indent=2,
            )
        )
        if result.final_code:
            print("--- solution.py ---")
            print(result.final_code)
        return 0 if result.success and not result.error else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
