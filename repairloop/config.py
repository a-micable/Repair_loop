from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    tavily_api_key: str
    max_iters: int
    sandbox_timeout: float
    runs_dir: str

    @property
    def has_nebius(self) -> bool:
        return bool(self.api_key)

    @property
    def has_tavily(self) -> bool:
        return bool(self.tavily_api_key)


def load_settings() -> Settings:
    return Settings(
        api_key=os.environ.get("NEBIUS_API_KEY", "").strip(),
        base_url=os.environ.get("NEBIUS_BASE_URL", DEFAULT_BASE_URL).strip(),
        model=os.environ.get("NEBIUS_MODEL", DEFAULT_MODEL).strip(),
        tavily_api_key=os.environ.get("TAVILY_API_KEY", "").strip(),
        max_iters=int(os.environ.get("REPAIRLOOP_MAX_ITERS", "5")),
        sandbox_timeout=float(os.environ.get("REPAIRLOOP_TIMEOUT", "12")),
        runs_dir=os.environ.get("REPAIRLOOP_RUNS_DIR", "runs"),
    )


# rough Token Factory list prices ($ / 1M tokens) for the UI meter — update if catalog changes
MODEL_PRICES = {
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B": (0.05, 0.20),
    "nvidia/Nemotron-3-Super-120B-A12B": (0.20, 0.60),
    "nvidia/Nemotron-3-Ultra-550B-A55B": (0.60, 1.80),
}


def estimate_cost_usd(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    inp, out = MODEL_PRICES.get(model, (0.10, 0.40))
    return (prompt_tokens * inp + completion_tokens * out) / 1_000_000
