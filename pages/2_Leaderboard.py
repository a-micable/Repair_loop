import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop.store import Store

st.set_page_config(page_title="Leaderboard · LabForge", layout="wide")
st.title("Leaderboard")

store = Store()
models = store.leaderboard()
tasks = store.task_stats()
recent = store.recent(40)

if not models:
    st.info("No runs recorded yet. Launch an agent from the Run page.")
else:
    st.subheader("by model")
    st.dataframe(models, use_container_width=True)
    st.subheader("by task")
    st.dataframe(tasks, use_container_width=True)

st.subheader("recent runs")
st.dataframe(recent, use_container_width=True)
