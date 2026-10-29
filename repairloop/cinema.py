"""Demo cinema — offline trajectories judges can replay without API keys."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterator


def cinema_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "fixtures" / "cinema"


def list_reels() -> list[dict[str, Any]]:
    root = cinema_dir()
    if not root.exists():
        return []
    out = []
    for path in sorted(root.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        out.append(
            {
                "id": path.stem,
                "path": str(path),
                "title": data.get("title") or path.stem,
                "task_id": data.get("task_id"),
                "model": data.get("model"),
                "success": data.get("success"),
                "frames": len(data.get("frames") or []),
            }
        )
    return out


def load_reel(reel_id: str) -> dict[str, Any]:
    path = cinema_dir() / f"{reel_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def iter_frames(reel: dict[str, Any], *, realtime: bool = False) -> Iterator[dict[str, Any]]:
    for frame in reel.get("frames") or []:
        if realtime:
            time.sleep(float(frame.get("delay_sec") or 0.35))
        yield frame


def write_reel(reel_id: str, payload: dict[str, Any]) -> Path:
    root = cinema_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{reel_id}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path
