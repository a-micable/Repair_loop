import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from repairloop.config import load_settings
from repairloop.dossier import build_dossier
from repairloop.tasks import list_tasks

st.set_page_config(page_title="Dossier · LabForge", layout="wide")
st.title("Research dossier")
st.caption("Skills + optional Tavily + Nemotron brief — the Tavily prize narrative.")

settings = load_settings()
tasks = list_tasks()
tid = st.selectbox("task", [t.id for t in tasks])
use_tavily = st.checkbox("call Tavily", value=settings.has_tavily)
call_model = st.checkbox("call Nemotron for brief", value=settings.has_nebius)

if st.button("build dossier", type="primary"):
    with st.spinner("building…"):
        d = build_dossier(tid, use_tavily=use_tavily, call_model=call_model)
    st.markdown(d.markdown())
    if d.tavily_raw:
        with st.expander("raw tavily json"):
            st.json(d.tavily_raw)
