# Contributing

## Add a task

1. Add `tasks/<id>.json` with `prompt`, `public_tests_hint`, `test_source`.
2. Add `oracles/<id>.py` that passes the grader.
3. Run:

```bash
python -m repairloop.eval --oracles-only
pytest -q
```

Or use the Streamlit **Bench / Author** page / `scripts/gen_extra_tasks.py` as a template.

## Style

- Graders must be stdlib-only in the sandbox.
- Prefer small, checkable tolerances.
- Don’t put truth parameters in `meta` visible to the agent.
