# Devpost — LabForge

**Track:** Coding & Agentic Engineering  
**Also claim:** Best Use of Tavily (if key enabled in demo)

## Project name
LabForge

## Tagline
Multi-stage STEM coding agents that must pass hidden graders — NVIDIA Nemotron on Nebius Token Factory, with Tavily-grounded research.

## Built with
Nebius Token Factory, NVIDIA Nemotron, Tavily, Python, FastAPI, Streamlit, SQLite, Docker

## Description

### Inspiration
I’ve been authoring terminal-bench style science/EE agent tasks. The gap I kept seeing in hackathon demos: models dump code and never face a real grader. LabForge closes that gap as a product.

### What it does
LabForge runs a **research → code → critic** pipeline on a suite of **15 STEM tasks** (circuits, arrays, DSP, control, sensors, heat equation, stats, robotics basics).

1. **Research** — retrieves local skill cards; optionally calls **Tavily** for formula grounding  
2. **Coder** — tool-using Nemotron agent (`write_file`, `run_python`, `run_tests`) on Nebius Token Factory  
3. **Grader** — hidden unit tests (stdlib sandbox)  
4. **Critic** — if failing, a reviewer pass feeds another coding burst  
5. **Telemetry** — JSONL transcripts + SQLite leaderboard (pass rate / tokens / cost by model)

Offline, `oracles/` + CI prove every grader is solvable without an LLM — so difficulty is intentional, not broken.

### How I built it
Python package `repairloop` (LabForge product surface): pipeline orchestrator, OpenAI-compatible Nebius client, workspace sandbox, skill retrieval, FastAPI, multipage Streamlit, pytest, GitHub Actions.

### Challenges
Tool-calling reliability across models (fallback fence-parse path), keeping the sandbox honest (no numpy shortcuts), and designing tasks that are hard for agents but trivial for a correct oracle.

### What’s next
Public task packs, harsher sandboxes, and model bake-offs (Nano vs Super) on the leaderboard.

## Nebius / NVIDIA
Runtime inference via Token Factory. Default `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`.

## Tavily
Research stage issues a targeted search (formulas/constants), injects snippets into the coder brief. Graders never need network — Tavily is for grounding, not cheating.

## Feedback
Token Factory’s OpenAI-compatible tools API made the agent loop portable. Nano is great for iteration; Super for tougher tasks. Would love a hackathon “Nemotron + tools” preset and clearer rate-limit guidance for multi-agent pipelines.

## Video (~2:30)
1. Home metrics (15 tasks, Nebius ready)  
2. `pytest` / oracle PASS scroll  
3. Run pipeline on RC task — show Tavily/skills research → tools → PASS  
4. Leaderboard page  
5. Flash FastAPI `/health` + `/tasks`  
6. Repo link
