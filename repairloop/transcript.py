from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _jsonable(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, Path):
        return str(obj)
    return obj


class Transcript:
    def __init__(self, runs_dir: Path, *, task_id: str, model: str) -> None:
        self.runs_dir = runs_dir
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
        self.path = self.runs_dir / f"{self.run_id}_{task_id}.jsonl"
        self.meta = {
            "run_id": self.run_id,
            "task_id": task_id,
            "model": model,
            "started_at": time.time(),
        }
        self._write({"type": "meta", **self.meta})

    def _write(self, row: dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, default=_jsonable) + "\n")

    def event(self, kind: str, **payload: Any) -> None:
        self._write({"type": kind, "t": time.time(), **payload})

    def finish(self, **payload: Any) -> Path:
        self._write({"type": "finish", "t": time.time(), **payload})
        return self.path
