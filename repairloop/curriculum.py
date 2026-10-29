"""Difficulty curriculum — unlock harder tasks after easier passes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .store import Store
from .tasks import Task, list_tasks

ORDER = {"easy": 0, "medium": 1, "hard": 2}


@dataclass
class CurriculumState:
    unlocked: list[str]
    locked: list[str]
    pass_by_diff: dict[str, int]
    next_recommended: str | None


def evaluate_curriculum(store: Store | None = None) -> CurriculumState:
    store = store or Store()
    tasks = list_tasks()
    recent = store.recent(500)
    passed_ids = {r["task_id"] for r in recent if r.get("success")}

    pass_by_diff = {"easy": 0, "medium": 0, "hard": 0}
    for t in tasks:
        if t.id in passed_ids:
            pass_by_diff[t.difficulty] = pass_by_diff.get(t.difficulty, 0) + 1

    # unlock policy: all easy always; medium after 3 easy passes; hard after 3 medium
    unlock_medium = pass_by_diff["easy"] >= 3
    unlock_hard = pass_by_diff["medium"] >= 3

    unlocked: list[str] = []
    locked: list[str] = []
    for t in tasks:
        if t.difficulty == "easy":
            unlocked.append(t.id)
        elif t.difficulty == "medium" and unlock_medium:
            unlocked.append(t.id)
        elif t.difficulty == "hard" and unlock_hard:
            unlocked.append(t.id)
        else:
            locked.append(t.id)

    # recommend easiest unfinished unlocked
    next_rec = None
    for t in sorted(tasks, key=lambda x: (ORDER.get(x.difficulty, 9), x.id)):
        if t.id in unlocked and t.id not in passed_ids:
            next_rec = t.id
            break

    return CurriculumState(
        unlocked=unlocked,
        locked=locked,
        pass_by_diff=pass_by_diff,
        next_recommended=next_rec,
    )


def as_dict(state: CurriculumState) -> dict[str, Any]:
    return {
        "unlocked": state.unlocked,
        "locked": state.locked,
        "pass_by_diff": state.pass_by_diff,
        "next_recommended": state.next_recommended,
        "unlock_rules": {
            "medium": ">=3 easy passes recorded",
            "hard": ">=3 medium passes recorded",
        },
    }
