# LabForge

**Nebius × NVIDIA Global AI Hackathon**  
**Track: Coding & Agentic Engineering**  
*(Best Use of Tavily eligible when `TAVILY_API_KEY` is set)*

LabForge is a STEM coding-agent workbench. Agents don’t get to “look done” — they have to **write code, run it, and pass a hidden grader**, the same idea behind terminal / agent eval harnesses, but as a product you can demo on Nebius Token Factory with **NVIDIA Nemotron**.

I built this after months of writing science/EE-style agent tasks. Chat demos that never hit a test harness don’t transfer. This one does.

## What it is

```
research (local skills + optional Tavily)
        ↓
tool-using coder  (write_file / run_python / run_tests)
        ↓
hidden STEM grader
        ↓
critic retry if still failing
        ↓
SQLite leaderboard + JSONL transcripts
```

- **15 graded tasks** across circuits, arrays, DSP, control, sensors, PDEs, stats, robotics basics  
- **Reference oracles** — every grader is proven solvable offline (CI runs this)  
- **Skill pack** — curated formula cards retrieved into the research stage  
- **FastAPI** + multipage **Streamlit** console  
- Token / rough cost meter on Nebius usage  

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env
# NEBIUS_API_KEY=...   from https://tokenfactory.nebius.com/
# TAVILY_API_KEY=...   optional, unlocks research web_search / Tavily prize path
```

## Run

```bash
# UI (pages in sidebar)
streamlit run app.py

# full prize-path pipeline on one task
python -m repairloop.cli run rc_step_response --pipeline

# single tool loop
python -m repairloop.cli run beamforming_delay

# HTTP API
uvicorn repairloop.api:app --port 8080
# POST /run  GET /leaderboard  GET /tasks  GET /skills?q=pid

# offline fairness proof (no API key)
python -m repairloop.eval --oracles-only
pytest -q
```

## Repo map

```
repairloop/     agent core (session, pipeline, tools, store, api)
tasks/          15 grader JSON specs
oracles/        known-good solutions
skills/         formula cards for research retrieval
pages/          Streamlit multipage UI
tests/          pytest
.github/        oracle CI
SUBMIT.md       Devpost paste pack
docs/           architecture notes
```

Default model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`  
Override with `NEBIUS_MODEL` (Super/Ultra when you have credits).

## Hackathon checklist

| Requirement | LabForge |
|---|---|
| Nebius Token Factory runtime | live chat.completions |
| NVIDIA open model | Nemotron |
| Coding & Agentic Engineering | writes + runs + tests + repairs |
| Tavily (optional prize) | research stage `web_search` |

## License

MIT
