SYSTEM = """You are RepairLoop, a scientific coding agent.

You solve small STEM tasks by writing Python that must pass a hidden grader.

Rules:
- stdlib only inside the sandbox (no numpy/scipy/network installs)
- put the graded entrypoints in solution.py unless the task says otherwise
- use tools: write_file, read_file, list_files, run_python, run_tests
- if web_search is available, use it only for formulas/constants — not to fetch finished code
- call run_tests when you think you are done; stop once it returns PASS
- keep changes small when repairing a failure
"""


def user_task(
    prompt: str,
    public_checks: str,
    *,
    tavily_on: bool,
    memory_block: str = "",
) -> str:
    extra = ""
    if tavily_on:
        extra = (
            "\nYou may call web_search for a quick formula check "
            "(e.g. RC charging equation, array delay geometry).\n"
        )
    mem = ""
    if memory_block.strip():
        mem = f"\n# Prior failure memory\n{memory_block}\n"
    return (
        f"# Task\n\n{prompt}\n\n"
        f"# Public checks (grader will enforce these)\n\n{public_checks}\n"
        f"{extra}{mem}\n"
        "Prefer replace_in_file for small fixes. Call run_tests when ready."
    )


def extract_python(text: str) -> str:
    t = (text or "").strip()
    if "```" not in t:
        return t
    parts = t.split("```")
    for i, chunk in enumerate(parts):
        if i % 2 == 0:
            continue
        body = chunk
        if body.startswith("python"):
            body = body[6:]
        elif body.startswith("py"):
            body = body[2:]
        return body.lstrip("\n").rstrip()
    return t
