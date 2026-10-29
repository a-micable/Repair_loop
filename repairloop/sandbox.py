from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RunResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


def _env(work: Path, extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {
        "HOME": str(work),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONNOUSERSITE": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
    }
    if extra:
        env.update(extra)
    return env


class Workspace:
    """Per-run scratch dir the agent can write into."""

    def __init__(self, root: Path | None = None) -> None:
        if root is None:
            root = Path(tempfile.mkdtemp(prefix="repairloop_ws_"))
            self._owned = True
        else:
            root.mkdir(parents=True, exist_ok=True)
            self._owned = False
        self.root = root.resolve()

    def cleanup(self) -> None:
        if self._owned and self.root.exists():
            shutil.rmtree(self.root, ignore_errors=True)

    def write(self, rel: str, content: str) -> Path:
        path = (self.root / rel).resolve()
        if not str(path).startswith(str(self.root)):
            raise ValueError(f"path escapes workspace: {rel}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read(self, rel: str) -> str:
        path = (self.root / rel).resolve()
        if not str(path).startswith(str(self.root)):
            raise ValueError(f"path escapes workspace: {rel}")
        return path.read_text(encoding="utf-8")

    def list_files(self) -> list[str]:
        out: list[str] = []
        for p in sorted(self.root.rglob("*")):
            if p.is_file():
                out.append(str(p.relative_to(self.root)))
        return out

    def run_python(
        self,
        rel: str = "solution.py",
        *,
        stdin: str = "",
        timeout: float = 8.0,
    ) -> RunResult:
        script = self.root / rel
        if not script.exists():
            return RunResult(False, 127, "", f"missing file: {rel}")
        try:
            proc = subprocess.run(
                [sys.executable, "-s", str(script)],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.root),
                env=_env(self.root),
            )
            return RunResult(
                ok=proc.returncode == 0,
                exit_code=proc.returncode,
                stdout=proc.stdout[-12000:],
                stderr=proc.stderr[-12000:],
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(
                False,
                124,
                (exc.stdout if isinstance(exc.stdout, str) else "")[-12000:],
                f"timeout after {timeout}s",
                timed_out=True,
            )

    def run_grader(self, test_source: str, *, timeout: float = 12.0) -> RunResult:
        self.write("tests.py", test_source)
        self.write(
            "_run_tests.py",
            "import traceback\n"
            "import tests\n"
            "try:\n"
            "    tests.run()\n"
            "    print('ALL_TESTS_PASSED')\n"
            "except Exception:\n"
            "    traceback.print_exc()\n"
            "    raise SystemExit(1)\n",
        )
        try:
            proc = subprocess.run(
                [sys.executable, "-s", str(self.root / "_run_tests.py")],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.root),
                env=_env(self.root, {"PYTHONPATH": str(self.root)}),
            )
            passed = proc.returncode == 0 and "ALL_TESTS_PASSED" in proc.stdout
            return RunResult(
                ok=passed,
                exit_code=proc.returncode,
                stdout=proc.stdout[-12000:],
                stderr=proc.stderr[-12000:],
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(
                False,
                124,
                (exc.stdout if isinstance(exc.stdout, str) else "")[-12000:],
                f"timeout after {timeout}s",
                timed_out=True,
            )
