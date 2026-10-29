import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop.config import load_settings
from repairloop.pipeline import run_pipeline
from repairloop.session import run_session
from repairloop.tasks import list_tasks

st.set_page_config(page_title="Run · LabForge", layout="wide")
st.title("Run agent")

settings = load_settings()
tasks = list_tasks()
by_id = {t.id: t for t in tasks}

mode = st.radio(
    "mode",
    ["full pipeline (research → code → critic)", "single tool loop"],
    horizontal=True,
)
use_tavily = st.checkbox("use Tavily in research", value=settings.has_tavily)
use_critic = st.checkbox("critic retry", value=True)
max_iters = st.slider("coding rounds", 1, 10, 5)

picked = st.selectbox(
    "task",
    [t.id for t in tasks],
    format_func=lambda i: f"{by_id[i].title} · {by_id[i].difficulty} · {', '.join(by_id[i].tags or [])}",
)
task = by_id[picked]

st.text(task.prompt)

if st.button("launch", type="primary"):
    if not settings.has_nebius:
        st.error("NEBIUS_API_KEY missing")
        st.stop()

    box = st.empty()
    lines: list[str] = []

    def on_progress(evt: dict) -> None:
        e = evt.get("event")
        if e == "pipeline":
            lines.append(f"stage: {evt.get('stage')}")
        elif e == "research":
            lines.append(f"research: {evt}")
        elif e == "tool":
            lines.append(f"tool {evt.get('name')}: {str(evt.get('result'))[:200]}")
        elif e == "critic":
            lines.append("critic:\n" + str(evt.get("text") or "")[:500])
        elif e == "thinking":
            lines.append(f"round {evt.get('iteration')}")
        box.text("\n".join(lines[-40:]))

    with st.spinner("running…"):
        if mode.startswith("full"):
            result = run_pipeline(
                task,
                max_iters=max_iters,
                use_tavily=use_tavily,
                use_critic=use_critic,
                on_progress=on_progress,
            )
        else:
            result = run_session(task, max_iters=max_iters, on_progress=on_progress)

    if result.success:
        st.success(f"PASS · {result.iterations} iters · ~${result.est_cost_usd:.5f}")
    else:
        st.warning(result.error or "FAIL")

    st.write(
        {
            "model": result.model,
            "tokens": result.prompt_tokens + result.completion_tokens,
            "transcript": result.transcript_path,
        }
    )
    st.code(result.final_code or "# empty", language="python")
