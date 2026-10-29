import streamlit as st

from repairloop.cinema import iter_frames, list_reels, load_reel

st.set_page_config(page_title="Cinema · LabForge", layout="wide")
st.title("Demo cinema")
st.caption("Offline trajectories — judges can watch a full repair loop without an API key.")

reels = list_reels()
if not reels:
    st.warning("No fixtures/cinema/*.json found")
    st.stop()

choice = st.selectbox(
    "reel",
    [r["id"] for r in reels],
    format_func=lambda i: next(
        f"{x['title']} · {'PASS' if x['success'] else 'FAIL'} · {x['frames']} frames"
        for x in reels
        if x["id"] == i
    ),
)
reel = load_reel(choice)

c1, c2, c3 = st.columns(3)
c1.metric("task", reel.get("task_id"))
c2.metric("model", str(reel.get("model", ""))[:28])
c3.metric("result", "PASS" if reel.get("success") else "FAIL")

play = st.button("play reel", type="primary")
box = st.empty()
code = st.empty()

if play:
    log = []
    for frame in iter_frames(reel, realtime=True):
        kind = frame.get("kind", "event")
        text = frame.get("text", "")
        log.append(f"[{kind}] {text}")
        box.code("\n\n".join(log[-12:]), language="text")
        if kind == "code":
            code.code(text, language="python")
    st.success("reel finished")
else:
    st.info("Press play to animate the trajectory.")
