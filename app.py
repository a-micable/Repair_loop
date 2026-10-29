"""LabForge home — multipage Streamlit entrypoint."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop import __version__
from repairloop.config import load_settings
from repairloop.tasks import list_tasks

st.set_page_config(page_title="LabForge", layout="wide")

st.markdown(
    """
    <style>
      .block-container { max-width: 1120px; padding-top: 1.2rem; }
      h1 { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 1.7rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = load_settings()
tasks = list_tasks()
by_diff = {}
for t in tasks:
    by_diff[t.difficulty] = by_diff.get(t.difficulty, 0) + 1

st.title("LabForge")
st.caption(
    f"v{__version__} · Nebius Token Factory · NVIDIA Nemotron · "
    "Coding & Agentic Engineering"
)

st.markdown(
    "STEM coding agents that must **pass a hidden grader** — "
    "research → tools → critic, with transcripts and bakeoffs."
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("tasks", len(tasks))
c2.metric("easy/med/hard", f"{by_diff.get('easy',0)}/{by_diff.get('medium',0)}/{by_diff.get('hard',0)}")
c3.metric("nebius", "ready" if settings.has_nebius else "need key")
c4.metric("tavily", "on" if settings.has_tavily else "off")
c5.metric("model", settings.model.split("/")[-1][:16])

st.markdown("### suite")
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
- **Run Agent** — pipeline or single loop  
- **Leaderboard** — pass rates / cost  
- **Skills & Replay** — skill pack + transcripts  
- **Bench / Author** — catalog + draft new tasks  

### offline proof
`python -m repairloop.eval --oracles-only && pytest -q`
"""
)
