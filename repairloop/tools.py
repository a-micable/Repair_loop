from __future__ import annotations

import json
from typing import Any

from . import tavily
from .config import Settings
from .patching import PatchError, apply_line_edits, apply_replace, summarize_diff
from .sandbox import Workspace


def openai_tool_schemas(allow_tavily: bool) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write/overwrite a text file in the workspace (usually solution.py).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                    },
                    "required": ["path", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "replace_in_file",
                "description": "Surgical edit: replace an exact substring in a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "solution.py"},
                        "old_string": {"type": "string"},
                        "new_string": {"type": "string"},
                        "replace_all": {"type": "boolean", "default": False},
                    },
                    "required": ["old_string", "new_string"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "replace_lines",
                "description": "Replace an inclusive 1-indexed line range in a file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "solution.py"},
                        "start_line": {"type": "integer"},
                        "end_line": {"type": "integer"},
                        "content": {"type": "string"},
                    },
                    "required": ["start_line", "end_line", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file from the workspace.",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files currently in the workspace.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_python",
                "description": "Execute a Python file in the workspace (default solution.py).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "solution.py"},
                        "stdin": {"type": "string", "default": ""},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "run_tests",
                "description": "Run the hidden grader against solution.py. Call this when ready.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    ]
    if allow_tavily:
        tools.append(
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": (
                        "Search via Tavily for a formula/constant reminder. "
                        "Do not search for finished solutions."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                },
            }
        )
    return tools


class ToolRouter:
    def __init__(
        self,
        workspace: Workspace,
        *,
        test_source: str,
        settings: Settings,
    ) -> None:
        self.ws = workspace
        self.test_source = test_source
        self.settings = settings
        self.last_grader_ok = False
        self.last_grader_stderr = ""
        self.history: list[dict[str, Any]] = []

    def dispatch(self, name: str, arguments: str | dict[str, Any]) -> str:
        if isinstance(arguments, str):
            try:
                args = json.loads(arguments or "{}")
            except json.JSONDecodeError:
                args = {}
        else:
            args = arguments or {}

        try:
            result = self._call(name, args)
        except Exception as exc:  # noqa: BLE001
            result = f"ERROR: {exc}"

        self.history.append({"tool": name, "args": args, "result": result[:4000]})
        return result

    def _call(self, name: str, args: dict[str, Any]) -> str:
        if name == "write_file":
            path = str(args.get("path") or "solution.py")
            content = str(args.get("content") or "")
            self.ws.write(path, content)
            return f"wrote {path} ({len(content)} bytes)"

        if name == "replace_in_file":
            path = str(args.get("path") or "solution.py")
            before = self.ws.read(path)
            try:
                after = apply_replace(
                    before,
                    str(args.get("old_string") or ""),
                    str(args.get("new_string") or ""),
                    replace_all=bool(args.get("replace_all") or False),
                )
            except PatchError as exc:
                return f"ERROR: {exc}"
            self.ws.write(path, after)
            return f"patched {path}: {summarize_diff(before, after)}"

        if name == "replace_lines":
            path = str(args.get("path") or "solution.py")
            before = self.ws.read(path)
            try:
                after = apply_line_edits(
                    before,
                    int(args["start_line"]),
                    int(args["end_line"]),
                    str(args.get("content") or ""),
                )
            except (KeyError, TypeError, ValueError, PatchError) as exc:
                return f"ERROR: {exc}"
            self.ws.write(path, after)
            return f"line-patched {path}: {summarize_diff(before, after)}"

        if name == "read_file":
            path = str(args.get("path") or "solution.py")
            return self.ws.read(path)

        if name == "list_files":
            files = self.ws.list_files()
            return "\n".join(files) if files else "(empty workspace)"

        if name == "run_python":
            path = str(args.get("path") or "solution.py")
            stdin = str(args.get("stdin") or "")
            r = self.ws.run_python(
                path, stdin=stdin, timeout=self.settings.sandbox_timeout
            )
            return (
                f"exit={r.exit_code} timed_out={r.timed_out}\n"
                f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
            )

        if name == "run_tests":
            r = self.ws.run_grader(
                self.test_source, timeout=self.settings.sandbox_timeout
            )
            self.last_grader_ok = r.ok
            self.last_grader_stderr = r.stderr
            status = "PASS" if r.ok else "FAIL"
            return (
                f"grader={status} exit={r.exit_code}\n"
                f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
            )

        if name == "web_search":
            q = str(args.get("query") or "").strip()
            if not q:
                return "ERROR: empty query"
            payload = tavily.search(q, self.settings.tavily_api_key)
            return tavily.format_for_model(payload)

        return f"ERROR: unknown tool {name}"
