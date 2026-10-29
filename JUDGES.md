# Judge one-pager — LabForge

**Track:** Coding & Agentic Engineering  
**Repo:** https://github.com/a-micable/Repair_loop  
**Differentiator:** agents must pass **hidden STEM graders** — not chat demos.

## Why this beats typical submissions

| Typical hackathon agent | LabForge |
|---|---|
| Dumps code once | write → run → test → **repair** |
| No proof of correctness | **45 oracle-backed tasks** + CI |
| Chat UI only | Cinema · Arena · Dossier · Bakeoff · API |
| “We used an LLM” | Nebius Token Factory + **Nemotron** (+ optional **Tavily**) |

## 60-second tour

1. Open Streamlit → **Demo Cinema** → play `rc_step_demo` (**no API key**)  
2. **Dossier** page — skills + Tavily research narrative  
3. **Run Agent** / **Arena** — live Nemotron on Token Factory  
4. `python -m repairloop.eval --oracles-only` — all PASS  

## Stack

Nebius Token Factory · NVIDIA Nemotron · Tavily · FastAPI · Streamlit · Docker Compose · Prometheus

## Offline proof

```bash
python -m repairloop.eval --oracles-only
pytest -q
```
