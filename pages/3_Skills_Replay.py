from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop.skills import format_skills, load_skills, retrieve

st.set_page_config(page_title="Skills · LabForge", layout="wide")
st.title("Skills & transcripts")

q = st.text_input("retrieve skills", placeholder="pid delay thermistor frobenius…")
if q.strip():
    hits = retrieve(q, k=5)
    st.markdown(format_skills(hits))
else:
    for s in load_skills():
        with st.expander(f"{s.title}  [{', '.join(s.tags)}]"):
            st.markdown(s.body)

st.markdown("---")
st.subheader("transcript replay")
runs = sorted(Path("runs").glob("*.jsonl"), reverse=True) if Path("runs").exists() else []
if not runs:
    st.write("no transcripts yet")
else:
    choice = st.selectbox("file", runs, format_func=lambda p: p.name)
    st.code(choice.read_text(encoding="utf-8")[:12000], language="json")
