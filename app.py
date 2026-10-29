"""LabForge home — multipage Streamlit entrypoint."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop import __version__
from repairloop.config import load_settings
from repairloop.tasks import list_tasks

st.set_page_config(page_title="LabForge", layout="wide", page_icon="🧪")

st.markdown(
    """
    <style>
      .block-container { max-width: 1100px; padding-top: 1.4rem; }
      h1 { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 1.7rem; }
      .hero { line-height: 1.55; opacity: 0.9; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = load_settings()
tasks = list_tasks()

st.title("LabForge")
st.caption(f"v{__version__} · Nebius Token Factory · NVIDIA Nemotron · Coding & Agentic Engineering")

st.markdown(
    f"""
<div class="hero">

STEM coding agents that have to **pass a hidden grader** — not chat demos that dump untested code.

Pipeline: **research** (skills + optional Tavily) → **tool-using coder** → **critic retry**.  
Inference on **Nebius Token Factory**. Default model **Nemotron Nano** (swap Super/Ultra in `.env`).

</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("tasks", len(tasks))
c2.metric("nebius", "ready" if settings.has_nebius else "need key")
c3.metric("tavily", "on" if settings.has_tavily else "off")
c4.metric("model", settings.model.split("/")[-1][:18])

st.markdown("### task suite")
st.dataframe(
    [
        {
            "id": t.id,
            "title": t.title,
            "difficulty": t.difficulty,
            "tags": ", ".join(t.tags or []),
        }
        for t in tasks
    ],
    use_container_width=True,
    hide_index=True,
)

st.markdown(
    """
### pages
- **Run Agent** — full pipeline or single tool loop  
- **Leaderboard** — pass rates / cost by model  
- **Skills & Replay** — local skill pack + JSONL transcripts  

### offline proof
```bash
python -m repairloop.eval --oracles-only
pytest -q
```
"""
)
