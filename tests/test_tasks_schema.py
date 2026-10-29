from repairloop.tasks import list_tasks


def test_all_tasks_load():
    tasks = list_tasks()
    assert len(tasks) >= 7
    ids = {t.id for t in tasks}
    assert "rc_step_response" in ids
    for t in tasks:
        assert t.prompt.strip()
        assert "def run" in t.test_source


def test_difficulties():
    allowed = {"easy", "medium", "hard"}
    for t in list_tasks():
        assert t.difficulty in allowed
