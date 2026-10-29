"""Local skill pack — tiny retrieval over curated STEM snippets (no embeddings dep)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    id: str
    title: str
    tags: list[str]
    body: str
    score: float = 0.0


def skills_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills"


def _tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9_]+", text.lower()) if len(t) > 2}


def load_skills() -> list[Skill]:
    out: list[Skill] = []
    root = skills_dir()
    if not root.exists():
        return out
    for path in sorted(root.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title = path.stem.replace("_", " ")
        tags: list[str] = []
        body = raw
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                meta, body = parts[1], parts[2]
                for line in meta.splitlines():
                    if line.strip().startswith("tags:"):
                        tags = [t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()]
                    if line.strip().startswith("title:"):
                        title = line.split(":", 1)[1].strip()
        out.append(Skill(id=path.stem, title=title, tags=tags, body=body.strip()))
    return out


def retrieve(query: str, *, k: int = 3) -> list[Skill]:
    q = _tokenize(query)
    ranked: list[Skill] = []
    for skill in load_skills():
        bag = _tokenize(skill.title + " " + " ".join(skill.tags) + " " + skill.body[:800])
        overlap = len(q & bag)
        tag_bonus = sum(1 for t in skill.tags if t.lower() in q)
        score = overlap + 2 * tag_bonus
        if score <= 0:
            continue
        ranked.append(
            Skill(
                id=skill.id,
                title=skill.title,
                tags=skill.tags,
                body=skill.body,
                score=float(score),
            )
        )
    ranked.sort(key=lambda s: s.score, reverse=True)
    return ranked[:k]


def format_skills(skills: list[Skill]) -> str:
    if not skills:
        return "(no skills matched)"
    blocks = []
    for s in skills:
        blocks.append(f"### {s.title} [{s.id}]\n{s.body}")
    return "\n\n".join(blocks)
