# Devpost — LabForge

**Track:** Coding & Agentic Engineering  
**Also claim:** Best Use of Tavily

## Name
LabForge

## Tagline
45-task STEM coding agents that must pass hidden graders — Demo Cinema, Nano-vs-Super Arena, and Tavily research dossiers on Nebius Token Factory / Nemotron.

## Built with
Nebius Token Factory, NVIDIA Nemotron, Tavily, Python, FastAPI, Streamlit, Docker, Prometheus

## Description

### The problem
Hackathon coding agents usually dump untested code. Judges can’t tell if anything works.

### What LabForge does
LabForge is a grader-first STEM agent workbench:

1. **Research dossier** — local skill cards + optional **Tavily** search + Nemotron brief  
2. **Tool-using coder** on Token Factory (`write_file`, surgical `replace_in_file`, `run_tests`, …)  
3. **Hidden unit graders** across **45** tasks (EE, DSP, control, optics, numerics, mechanics, stats…)  
4. **Critic retry** + **failure memory** + **skill distillation** on PASS  
5. **Demo Cinema** — offline trajectories so judges see a full repair loop **without keys**  
6. **Model Arena** — Nano vs Super head-to-head on the same grader  
7. Bakeoff CLI, Prometheus metrics, FastAPI, docker-compose, curriculum unlocks  

Every task has a reference oracle; CI runs `eval --oracles-only`.

### Nebius / NVIDIA
Live inference via Token Factory. Default Nemotron Nano; Super/Ultra configurable.

### Tavily
Dossier + research stage issue targeted formula queries (not solution scraping). Graders stay offline.

## Feedback
Token Factory tool-calling made the repair loop practical. Demo Cinema is how we keep judging honest when credits/keys are awkward. A Nemotron+tools hackathon preset would help.

## Video script
1. JUDGES.md / home tags (45 tasks, cinema, arena)  
2. **Demo Cinema** play `rc_step_demo`  
3. **Dossier** with Tavily  
4. Live **Run** or **Arena** snippet  
5. Oracle PASS in terminal + GitHub
