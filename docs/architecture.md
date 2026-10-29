# Architecture

```
          ┌────────────┐
 user ──► │ Streamlit /│
          │ CLI        │
          └─────┬──────┘
                │
                ▼
        repairloop.session
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
  Nebius     ToolRouter  Workspace
  Nemotron   (tools)     (sandbox)
     │          │          │
     │          ├ write_file / read_file
     │          ├ run_python
     │          ├ run_tests ──► hidden grader from tasks/*.json
     │          └ web_search (optional Tavily)
     │
     └── usage meter + JSONL transcript in runs/
```

Graders never leave the machine. Inference always goes to Token Factory when the agent runs. Oracles under `oracles/` are only for offline fairness checks (`repairloop.eval --oracles-only`).
