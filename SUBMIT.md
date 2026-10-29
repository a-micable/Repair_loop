# Devpost — LabForge

**Track:** Coding & Agentic Engineering  
**Also:** Best Use of Tavily (if enabled)

## Name
LabForge

## Tagline
A 35-task STEM coding-agent workbench: research → tools → hidden grader → critic, on NVIDIA Nemotron via Nebius Token Factory.

## Built with
Nebius Token Factory, NVIDIA Nemotron, Tavily, Python, FastAPI, Streamlit, Docker, Prometheus

## Description

### What it does
LabForge is a full agent workbench for scientific coding tasks. Agents must write Python, run it, and pass hidden graders across **35** oracle-backed tasks (circuits, DSP, control, optics, numerics, stats, algorithms).

Pipeline: **skills + optional Tavily research** → **tool-using Nemotron coder** (write/replace/run/test) → **critic retry** → SQLite leaderboard + JSONL transcripts + Prometheus metrics. Includes bakeoff CLI, FastAPI, docker-compose, and a task authoring UI.

### Why it matters
Most hackathon “coding agents” dump untested code. LabForge mirrors terminal-bench style evaluation: **no PASS from the grader, no win.**

### Nebius / NVIDIA
Live Token Factory chat completions. Default Nemotron Nano; Super/Ultra via env.

### Tavily
Research stage issues a targeted formula search and injects results into the coder brief. Graders stay offline.

## Feedback
Token Factory’s OpenAI-compatible tools API made multi-tool repair practical. Nano is great for iteration cost; bakeoff mode compares models on the same suite. A hackathon preset for Nemotron+tools would help newcomers.

## Video
1. Home (35 tasks)  
2. Oracle PASS scroll  
3. Pipeline run with tools  
4. Leaderboard + /metrics  
5. Repo
