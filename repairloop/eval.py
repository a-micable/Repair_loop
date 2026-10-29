"""Offline oracle check + optional live agent bench."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from .sandbox import Workspace
from .tasks import list_tasks


ROOT = Path(__file__).resolve().parent.parent
ORACLES = ROOT / "oracles"


def check_oracles() -> int:
    failures = 0
    for task in list_tasks():
        oracle = ORACLES / f"{task.id}.py"
        if not oracle.exists():
            print(f"[SKIP] {task.id}: no oracle")
            continue
        ws = Workspace()
        try:
            ws.write("solution.py", oracle.read_text(encoding="utf-8"))
            result = ws.run_grader(task.test_source, timeout=20.0)
            tag = "PASS" if result.ok else "FAIL"
            print(f"[{tag}] oracle {task.id}")
            if not result.ok:
                failures += 1
                print(result.stdout)
                print(result.stderr)
        finally:
            ws.cleanup()
    return failures


def run_agent_suite(task_ids: list[str] | None, max_iters: int) -> int:
    from .session import run_session

    tasks = list_tasks()
    if task_ids:
        wanted = set(task_ids)
        tasks = [t for t in tasks if t.id in wanted]

    rows = []
    fails = 0
    for task in tasks:
        print(f"== agent {task.id} ==")
        result = run_session(task, max_iters=max_iters)
        rows.append(
            {
                "task": task.id,
                "success": result.success,
                "iters": result.iterations,
                "model": result.model,
                "prompt_tokens": result.prompt_tokens,
                "completion_tokens": result.completion_tokens,
                "est_cost_usd": result.est_cost_usd,
                "error": result.error,
            }
        )
        print(
            " success=",
            result.success,
            " iters=",
            result.iterations,
            " tokens=",
            result.prompt_tokens + result.completion_tokens,
            " cost~$",
            round(result.est_cost_usd, 5),
        )
        if not result.success:
            fails += 1

    out = ROOT / "runs" / "suite_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", out)
    return fails


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="repairloop-eval")
    p.add_argument("--oracles-only", action="store_true")
    p.add_argument("--agent", action="store_true", help="needs NEBIUS_API_KEY")
    p.add_argument("--task", action="append", default=[])
    p.add_argument("--iters", type=int, default=5)
    args = p.parse_args(argv)

    rc = 0
    if args.oracles_only or not args.agent:
        rc += check_oracles()
    if args.agent:
        rc += run_agent_suite(args.task or None, args.iters)
    return 1 if rc else 0


if __name__ == "__main__":
    raise SystemExit(main())
