# LabForge

**Nebius × NVIDIA Global AI Hackathon** · Track: **Coding & Agentic Engineering**  
Tavily-eligible when `TAVILY_API_KEY` is set.

LabForge is a full STEM **coding-agent workbench**: research → tool-using coder → hidden grader → critic, with transcripts, leaderboards, bakeoffs, and a 35-task oracle-backed suite.

Built from the same instincts as terminal / agent eval harnesses — demos that never call `run_tests` don’t count.

## Highlights (v1.0)

- **35 graded tasks** (EE, DSP, control, optics, numerics, stats, algorithms…)
- **Oracle CI** — every grader is solvable offline
- **Pipeline** — skills + optional Tavily research → tools (`write_file`, `replace_in_file`, `run_tests`, …) → critic retry
- **Failure memory** across runs
- **Prometheus metrics** + SQLite leaderboard
- **Bakeoff** CLI for multi-model comparisons
- **FastAPI** + multipage **Streamlit** + **docker-compose**
- Task authoring UI + generator script

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env   # set NEBIUS_API_KEY (+ optional TAVILY_API_KEY)

streamlit run app.py
# or
uvicorn repairloop.api:app --port 8080
docker compose up --build
```

```bash
python -m repairloop.cli tasks
python -m repairloop.cli run rc_step_response --pipeline
python -m repairloop.eval --oracles-only
python -m repairloop.cli bench --pipeline --task rc_step_response --task thermistor_beta
pytest -q
```

See `docs/TASK_CATALOG.md`, `docs/architecture.md`, `SUBMIT.md`.

## Stack

Nebius Token Factory · NVIDIA Nemotron · Tavily (optional) · Python 3.11+

## License

MIT
