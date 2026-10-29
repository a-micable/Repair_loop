"""Lightweight Prometheus text metrics for LabForge."""

from __future__ import annotations

import threading
import time
from typing import Any

_lock = threading.Lock()
_counters: dict[str, float] = {
    "labforge_runs_total": 0,
    "labforge_runs_success_total": 0,
    "labforge_runs_fail_total": 0,
    "labforge_tokens_prompt_total": 0,
    "labforge_tokens_completion_total": 0,
    "labforge_tool_calls_total": 0,
}
_gauges: dict[str, float] = {
    "labforge_last_run_success": 0,
    "labforge_last_run_cost_usd": 0,
}
_started = time.time()


def inc(name: str, value: float = 1.0) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0.0) + value


def set_gauge(name: str, value: float) -> None:
    with _lock:
        _gauges[name] = value


def observe_run(
    *,
    success: bool,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    tool_calls: int,
) -> None:
    inc("labforge_runs_total")
    inc("labforge_runs_success_total" if success else "labforge_runs_fail_total")
    inc("labforge_tokens_prompt_total", prompt_tokens)
    inc("labforge_tokens_completion_total", completion_tokens)
    inc("labforge_tool_calls_total", tool_calls)
    set_gauge("labforge_last_run_success", 1.0 if success else 0.0)
    set_gauge("labforge_last_run_cost_usd", cost_usd)


def render_prometheus() -> str:
    lines = [
        f"# HELP labforge_up LabForge process up",
        f"# TYPE labforge_up gauge",
        f"labforge_up 1",
        f"# HELP labforge_uptime_seconds Uptime",
        f"# TYPE labforge_uptime_seconds gauge",
        f"labforge_uptime_seconds {time.time() - _started:.3f}",
    ]
    with _lock:
        for k, v in sorted(_counters.items()):
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {v}")
        for k, v in sorted(_gauges.items()):
            lines.append(f"# TYPE {k} gauge")
            lines.append(f"{k} {v}")
    return "\n".join(lines) + "\n"


def snapshot() -> dict[str, Any]:
    with _lock:
        return {
            "counters": dict(_counters),
            "gauges": dict(_gauges),
            "uptime_sec": time.time() - _started,
        }
