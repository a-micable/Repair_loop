"""Research dossier — structured brief for UI / Tavily prize narrative."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .config import load_settings
from .llm import NebiusClient
from .skills import format_skills, retrieve
from .tasks import Task, load_task
from .tavily import format_for_model, search


@dataclass
class Dossier:
    task_id: str
    skills: list[str] = field(default_factory=list)
    tavily_query: str = ""
    tavily_used: bool = False
    tavily_raw: dict[str, Any] = field(default_factory=dict)
    model_brief: str = ""
    bullets: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def markdown(self) -> str:
        lines = [
            f"# Research dossier — `{self.task_id}`",
            "",
            "## Skill pack",
            ", ".join(self.skills) if self.skills else "(none)",
            "",
            "## Tavily",
            f"query: `{self.tavily_query or 'n/a'}`",
            f"used: {self.tavily_used}",
            "",
            "## Brief",
            self.model_brief or "(no model brief)",
        ]
        if self.bullets:
            lines.append("")
            lines.append("## Checklist")
            lines.extend(f"- {b}" for b in self.bullets)
        return "\n".join(lines) + "\n"


def build_dossier(
    task: Task | str,
    *,
    use_tavily: bool | None = None,
    call_model: bool = True,
) -> Dossier:
    if isinstance(task, str):
        task = load_task(task)
    settings = load_settings()
    tavily_on = settings.has_tavily if use_tavily is None else use_tavily

    skills = retrieve(task.prompt + " " + " ".join(task.tags or []), k=4)
    dossier = Dossier(
        task_id=task.id,
        skills=[s.id for s in skills],
    )

    raw: dict[str, Any] = {}
    if tavily_on and settings.has_tavily:
        q = f"{task.title} formula equation site:edu OR site:wikipedia.org"
        dossier.tavily_query = q
        dossier.tavily_used = True
        raw = search(q, settings.tavily_api_key)
        dossier.tavily_raw = raw

    if call_model and settings.has_nebius:
        client = NebiusClient(settings)
        reply = client.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "Produce a short research brief for a coding agent. "
                        "Return markdown with 4-8 checklist bullets of formulas/pitfalls. No code."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"# Task\n{task.prompt}\n\n"
                        f"# Skills\n{format_skills(skills)}\n\n"
                        f"# Web\n{format_for_model(raw) if raw else '(no web)'}\n"
                    ),
                },
            ],
            temperature=0.2,
            max_tokens=700,
        )
        dossier.model_brief = reply["content"]
        # crude bullet extract
        for line in dossier.model_brief.splitlines():
            s = line.strip()
            if s.startswith(("-", "*", "•")):
                dossier.bullets.append(s.lstrip("-*• ").strip())
    else:
        # offline dossier from skills alone
        dossier.model_brief = format_skills(skills)
        dossier.bullets = [s.title for s in skills]

    return dossier
