"""Optional Tavily search — stdlib only so the core agent doesn't need httpx."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


def search(query: str, api_key: str, *, max_results: int = 4) -> dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "TAVILY_API_KEY not set"}
    body = json.dumps(
        {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": True,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return {"ok": False, "error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}

    hits = []
    for item in data.get("results") or []:
        hits.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": (item.get("content") or "")[:500],
            }
        )
    return {"ok": True, "answer": data.get("answer"), "results": hits}


def format_for_model(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2)[:6000]
