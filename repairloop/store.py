"""SQLite run store + leaderboard."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY,
  task_id TEXT NOT NULL,
  model TEXT NOT NULL,
  success INTEGER NOT NULL,
  iterations INTEGER NOT NULL,
  prompt_tokens INTEGER NOT NULL,
  completion_tokens INTEGER NOT NULL,
  est_cost_usd REAL NOT NULL,
  pipeline TEXT NOT NULL,
  transcript_path TEXT,
  created_at REAL NOT NULL,
  meta_json TEXT
);
CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_runs_model ON runs(model);
"""


class Store:
    def __init__(self, path: str | Path = "runs/labforge.sqlite") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._conn() as conn:
            conn.executescript(SCHEMA)

    def record_run(self, row: dict[str, Any]) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs
                (id, task_id, model, success, iterations, prompt_tokens, completion_tokens,
                 est_cost_usd, pipeline, transcript_path, created_at, meta_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    row["task_id"],
                    row["model"],
                    1 if row.get("success") else 0,
                    int(row.get("iterations") or 0),
                    int(row.get("prompt_tokens") or 0),
                    int(row.get("completion_tokens") or 0),
                    float(row.get("est_cost_usd") or 0.0),
                    row.get("pipeline") or "single",
                    row.get("transcript_path"),
                    float(row.get("created_at") or time.time()),
                    json.dumps(row.get("meta") or {}),
                ),
            )

    def recent(self, limit: int = 30) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    def leaderboard(self) -> list[dict[str, Any]]:
        """Pass rate and median iters by model."""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT model,
                       COUNT(*) AS n,
                       SUM(success) AS passes,
                       AVG(iterations) AS avg_iters,
                       SUM(prompt_tokens + completion_tokens) AS tokens,
                       SUM(est_cost_usd) AS cost
                FROM runs
                GROUP BY model
                ORDER BY passes * 1.0 / COUNT(*) DESC, avg_iters ASC
                """
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            d["pass_rate"] = (d["passes"] / d["n"]) if d["n"] else 0.0
            out.append(d)
        return out

    def task_stats(self) -> list[dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT task_id,
                       COUNT(*) AS n,
                       SUM(success) AS passes,
                       AVG(iterations) AS avg_iters
                FROM runs
                GROUP BY task_id
                ORDER BY task_id
                """
            ).fetchall()
        return [dict(r) for r in rows]
