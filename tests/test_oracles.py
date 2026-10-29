from pathlib import Path

from repairloop.sandbox import Workspace
from repairloop.tasks import list_tasks

ROOT = Path(__file__).resolve().parents[1]
ORACLES = ROOT / "oracles"


def test_oracles_pass_graders():
    missing = []
    failed = []
    for task in list_tasks():
        oracle = ORACLES / f"{task.id}.py"
        if not oracle.exists():
            missing.append(task.id)
            continue
        ws = Workspace()
        try:
            ws.write("solution.py", oracle.read_text(encoding="utf-8"))
            result = ws.run_grader(task.test_source, timeout=25.0)
            if not result.ok:
                failed.append((task.id, result.stderr, result.stdout))
        finally:
            ws.cleanup()
    assert not missing, f"missing oracles: {missing}"
    assert not failed, failed
