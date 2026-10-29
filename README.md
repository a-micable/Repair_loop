# LabForge

**Nebius × NVIDIA Global AI Hackathon** · **Coding & Agentic Engineering**  
Tavily-eligible · Judge one-pager: [`JUDGES.md`](JUDGES.md)

> Agents that must **pass a hidden STEM grader** — with a Demo Cinema so judges can watch a PASS **without an API key**.

## Why this wins attention

| Feature | What judges see |
|---|---|
| **Demo Cinema** | Offline repair trajectories (no key) |
| **Model Arena** | Nano vs Super, same grader, winner by PASS/iters/cost |
| **Research Dossier** | Skills + **Tavily** + Nemotron brief |
| **45 tasks** | Oracle-backed; CI proves fairness |
| **Skill distill** | PASSes become reusable skill cards |
| **Curriculum** | Harder tiers unlock after easy wins |
| **Bakeoff / Prometheus / API** | Real eval infrastructure |

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
cp .env.example .env   # NEBIUS_API_KEY=...  TAVILY_API_KEY=...

streamlit run app.py
# pages: Run · Leaderboard · Skills · Bench · Cinema · Arena · Dossier

python -m repairloop.eval --oracles-only
pytest -q
docker compose up --build
```

## Stack

Nebius Token Factory · NVIDIA Nemotron · Tavily · FastAPI · Streamlit · Docker

## License

MIT
