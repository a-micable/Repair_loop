"""RepairLoop — STEM coding agent on Nebius Token Factory / NVIDIA Nemotron."""

__version__ = "0.5.0"

# keep import light; session pulls openai/httpx
__all__ = ["__version__", "AgentResult", "run_session"]


def __getattr__(name: str):
    if name in {"AgentResult", "run_session"}:
        from .session import AgentResult, run_session

        return {"AgentResult": AgentResult, "run_session": run_session}[name]
    raise AttributeError(name)
