"""Apply unified-diff style patches to workspace files (agent edit tool)."""

from __future__ import annotations

import re
from pathlib import Path


class PatchError(ValueError):
    pass


def apply_replace(text: str, old: str, new: str, *, replace_all: bool = False) -> str:
    if old not in text:
        raise PatchError("old_string not found in file")
    if not replace_all and text.count(old) > 1:
        raise PatchError("old_string is ambiguous; set replace_all or add context")
    if replace_all:
        return text.replace(old, new)
    return text.replace(old, new, 1)


def apply_line_edits(text: str, start_line: int, end_line: int, replacement: str) -> str:
    """1-indexed inclusive line replace."""
    lines = text.splitlines(keepends=True)
    n = len(lines)
    if start_line < 1 or end_line > n or start_line > end_line:
        raise PatchError(f"bad line range {start_line}-{end_line} for {n} lines")
    out = lines[: start_line - 1]
    if replacement and not replacement.endswith("\n") and end_line < n:
        replacement += "\n"
    out.append(replacement)
    out.extend(lines[end_line:])
    return "".join(out)


def summarize_diff(before: str, after: str, *, max_lines: int = 40) -> str:
    b = before.splitlines()
    a = after.splitlines()
    # cheap summary — not a full Myers diff
    if before == after:
        return "(no change)"
    return (
        f"before_lines={len(b)} after_lines={len(a)} "
        f"delta_chars={len(after) - len(before)}"
    )
