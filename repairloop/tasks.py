from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Task:
    id: str
    title: str
    difficulty: str
    prompt: str
    public_tests_hint: str
    test_source: str
    track_fit: str = "Coding & Agentic Engineering"
    tags: list[str] | None = None
    raw: dict[str, Any] | None = None


def tasks_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "tasks"


def load_task(task_id: str) -> Task:
    path = tasks_dir() / f"{task_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"unknown task: {task_id}")
    return task_from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_tasks() -> list[Task]:
    out: list[Task] = []
    for path in sorted(tasks_dir().glob("*.json")):
        out.append(task_from_dict(json.loads(path.read_text(encoding="utf-8"))))
    return out


def task_from_dict(data: dict[str, Any]) -> Task:
    required = ["id", "title", "difficulty", "prompt", "public_tests_hint", "test_source"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"task missing keys: {missing}")
    return Task(
        id=data["id"],
        title=data["title"],
        difficulty=data["difficulty"],
        prompt=data["prompt"],
        public_tests_hint=data["public_tests_hint"],
        test_source=data["test_source"],
        track_fit=data.get("track_fit", "Coding & Agentic Engineering"),
        tags=list(data.get("tags") or []),
        raw=data,
    )
