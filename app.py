"""LabForge home."""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop import __version__
from repairloop.cinema import list_reels
from repairloop.config import load_settings
from repairloop.curriculum import as_dict, evaluate_curriculum
from repairloop.tasks import list_tasks

st.set_page_config(page_title="LabForge", layout="wide")

st.markdown(
    """
    <style>
      .block-container { max-width: 1140px; padding-top: 1rem; }
      h1 { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 1.75rem;
           letter-spacing: -0.03em; }
      .tag { display:inline-block; border:1px solid #444; padding:0.15rem 0.5rem;
             margin-right:0.35rem; font-size:0.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = load_settings()
tasks = list_tasks()
reels = list_reels()
cur = as_dict(evaluate_curriculum())
by_diff = {}
for t in tasks:
    by_diff[t.difficulty] = by_diff.get(t.difficulty, 0) + 1

st.title("LabForge")
st.caption(
    f"v{__version__} · Nebius Token Factory · NVIDIA Nemotron · grader-first STEM agents"
)

st.markdown(
    '<span class="tag">45 tasks</span>'
    '<span class="tag">demo cinema</span>'
    '<span class="tag">model arena</span>'
    '<span class="tag">Tavily dossier</span>'
    '<span class="tag">skill distill</span>',
    unsafe_allow_html=True,
)

st.markdown(
    "Most coding-agent demos never face a test harness. LabForge does: "
    "**research → tools → hidden grader → critic**, with offline cinema for judges "
    "and a live Nano-vs-Super arena."
)

a, b, c, d, e = st.columns(5)
a.metric("tasks", len(tasks))
b.metric("E/M/H", f"{by_diff.get('easy',0)}/{by_diff.get('medium',0)}/{by_diff.get('hard',0)}")
c.metric("nebius", "ready" if settings.has_nebius else "need key")
d.metric("tavily", "on" if settings.has_tavily else "off")
e.metric("cinema reels", len(reels))

st.markdown("### start here (judges)")
st.markdown(
    "1. **Demo Cinema** — watch a PASS with no API key  \n"
    "2. **Dossier** — Tavily + skills research brief  \n"
    "3. **Arena** — Nano vs Super on one grader  \n"
    "4. `JUDGES.md` in the repo — one-pager"
)

st.markdown("### curriculum")
st.write(
    {
        "unlocked": len(cur["unlocked"]),
        "locked": len(cur["locked"]),
        "passes": cur["pass_by_diff"],
        "next": cur["next_recommended"],
    }
)

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
