"""Cross-run failure memory — surfaces past grader errors for similar tasks."""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any


def _path(runs_dir: str | Path) -> Path:
    p = Path(runs_dir) / "failure_memory.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def remember_failure(
    runs_dir: str | Path,
    *,
    task_id: str,
    tags: list[str],
    stderr: str,
    hint: str = "",
) -> None:
    row = {
        "t": time.time(),
        "task_id": task_id,
        "tags": tags,
        "stderr": (stderr or "")[:1500],
        "hint": (hint or "")[:800],
    }
    with _path(runs_dir).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def recall(
    runs_dir: str | Path,
    *,
    task_id: str,
    tags: list[str] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    path = _path(runs_dir)
    if not path.exists():
        return []
    tags_l = {t.lower() for t in (tags or [])}
    hits: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        score = 0
        if row.get("task_id") == task_id:
            score += 3
        row_tags = {str(t).lower() for t in (row.get("tags") or [])}
        score += len(tags_l & row_tags)
        if score:
            hits.append({**row, "_score": score})
    hits.sort(key=lambda r: (r["_score"], r.get("t", 0)), reverse=True)
    return hits[:limit]


def format_memory(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "(no prior failures recalled)"
    parts = []
    for r in rows:
        err = re.sub(r"\s+", " ", str(r.get("stderr") or ""))[:240]
        parts.append(
            f"- task={r.get('task_id')} hint={r.get('hint') or 'n/a'} stderr={err}"
        )
    return "\n".join(parts)
