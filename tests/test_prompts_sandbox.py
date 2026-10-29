from repairloop.prompts import extract_python
from repairloop.sandbox import Workspace


def test_extract_plain():
    assert extract_python("print(1)") == "print(1)"


def test_extract_fence():
    assert "print(1)" in extract_python("```python\nprint(1)\n```")


def test_workspace_path_guard():
    ws = Workspace()
    try:
        try:
            ws.write("../escape.py", "x=1")
            raised = False
        except ValueError:
            raised = True
        assert raised
    finally:
        ws.cleanup()


def test_run_python_ok():
    ws = Workspace()
    try:
        ws.write("solution.py", "print('hi')\n")
        r = ws.run_python()
        assert r.ok
        assert "hi" in r.stdout
    finally:
        ws.cleanup()
