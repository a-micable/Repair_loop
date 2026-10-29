from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI

from .config import Settings, load_settings


@dataclass
class UsageMeter:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    calls: int = 0
    raw_events: list[dict[str, Any]] = field(default_factory=list)

    def add(self, usage: Any, *, model: str) -> None:
        if usage is None:
            return
        pt = int(getattr(usage, "prompt_tokens", 0) or 0)
        ct = int(getattr(usage, "completion_tokens", 0) or 0)
        self.prompt_tokens += pt
        self.completion_tokens += ct
        self.calls += 1
        self.raw_events.append(
            {"model": model, "prompt_tokens": pt, "completion_tokens": ct}
        )

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class NebiusClient:
    """OpenAI-compatible client pinned to Nebius Token Factory."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()
        if not self.settings.api_key:
            raise RuntimeError(
                "NEBIUS_API_KEY missing — create a key at tokenfactory.nebius.com"
            )
        self.client = OpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.api_key,
        )
        self.meter = UsageMeter()

    @property
    def model(self) -> str:
        return self.settings.model

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        resp = self.client.chat.completions.create(**kwargs)
        self.meter.add(resp.usage, model=self.model)
        msg = resp.choices[0].message

        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append(
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments or "{}",
                    }
                )

        return {
            "role": "assistant",
            "content": (msg.content or "").strip(),
            "tool_calls": tool_calls,
            "raw": msg,
        }
