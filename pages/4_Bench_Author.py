import json
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop.tasks import list_tasks, tasks_dir

st.set_page_config(page_title="Bench · LabForge", layout="wide")
st.title("Task catalog & authoring")

tasks = list_tasks()
st.metric("tasks loaded", len(tasks))

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

st.markdown("### draft a new task JSON")
st.caption("Saved under tasks/ when you click write (local only).")

with st.form("author"):
    tid = st.text_input("id", "my_task")
    title = st.text_input("title", "My task")
    difficulty = st.selectbox("difficulty", ["easy", "medium", "hard"])
    tags = st.text_input("tags (comma)", "math, ee")
    prompt = st.text_area("prompt", height=160)
    hint = st.text_area("public_tests_hint", height=80)
    test_source = st.text_area(
        "test_source",
        value="import solution\n\ndef run():\n    assert hasattr(solution, 'main') or True\n",
        height=160,
    )
    submitted = st.form_submit_button("write task json")

if submitted:
    if not tid.isidentifier() and not all(c.isalnum() or c == "_" for c in tid):
        st.error("id should be snake_case / alphanumeric")
    else:
        payload = {
            "id": tid,
            "title": title,
            "difficulty": difficulty,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "prompt": prompt,
            "public_tests_hint": hint,
            "test_source": test_source,
            "track_fit": "Coding & Agentic Engineering",
        }
        path = tasks_dir() / f"{tid}.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        st.success(f"wrote {path}")

st.markdown("### bakeoff CLI")
st.code(
    "python -m repairloop.bench --pipeline --task rc_step_response "
    "--model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    language="bash",
)
