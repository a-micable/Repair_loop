"""Distill successful solutions into reusable skill cards."""

from __future__ import annotations

import re
import time
from pathlib import Path

from .skills import skills_dir
from .tasks import load_task


def distill_success(
    *,
    task_id: str,
    code: str,
    model: str,
) -> Path:
    task = load_task(task_id)
    # keep skills short — formula-ish comments + signature hints
    sigs = re.findall(r"^def\s+(\w+)\(.*\):", code, flags=re.M)
    body = [
        f"---",
        f"title: Distilled — {task.title}",
        f"tags: {', '.join((task.tags or []) + ['distilled'])}",
        f"---",
        "",
        f"Auto-distilled from a PASS on `{task_id}` using `{model}` at {time.strftime('%Y-%m-%d')}.",
        "",
        f"Entry points: {', '.join(sigs) if sigs else '(see code)'}",
        "",
        "```python",
        code.strip()[:2500],
        "```",
        "",
        "Use as a pattern reminder — do not paste blindly into graded runs.",
    ]
    root = skills_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"distilled_{task_id}.md"
    path.write_text("\n".join(body) + "\n", encoding="utf-8")
    return path
