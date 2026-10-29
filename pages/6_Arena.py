import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop.arena import run_arena
from repairloop.config import load_settings
from repairloop.tasks import list_tasks

st.set_page_config(page_title="Arena · LabForge", layout="wide")
st.title("Model arena")
st.caption("Same task · two Nemotron models · grader decides the winner.")

settings = load_settings()
tasks = list_tasks()
by_id = {t.id: t for t in tasks}

left = st.text_input("left model", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B")
right = st.text_input(
    "right model",
    "nvidia/Nemotron-3-Super-120B-A12B",
)
task_id = st.selectbox("task", [t.id for t in tasks], index=min(5, len(tasks) - 1))
pipeline = st.checkbox("use full pipeline", value=True)
iters = st.slider("iters/side", 1, 6, 3)

if st.button("fight", type="primary"):
    if not settings.has_nebius:
        st.error("NEBIUS_API_KEY required for live arena")
        st.stop()
    log = st.empty()
    lines = []

    def on_progress(evt):
        if evt.get("event") == "arena":
            lines.append(str(evt))
            log.text("\n".join(lines[-20:]))

    with st.spinner("arena running…"):
        result = run_arena(
            by_id[task_id],
            left_model=left,
            right_model=right,
            pipeline=pipeline,
            max_iters=iters,
            on_progress=on_progress,
        )

    st.subheader(f"winner: {result.winner}")
    st.write(result.reason)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### left · `{result.left_model}`")
        st.json({k: v for k, v in result.left.items() if k != "final_code"})
        st.code(result.left.get("final_code") or "", language="python")
    with col_b:
        st.markdown(f"### right · `{result.right_model}`")
        st.json({k: v for k, v in result.right.items() if k != "final_code"})
        st.code(result.right.get("final_code") or "", language="python")
