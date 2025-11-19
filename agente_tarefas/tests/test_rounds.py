import pytest

from agente_tarefas.utils.rounds import (
    build_initial_tasks,
    collect_new_tasks,
    select_completed_task,
    split_tasks,
)


def test_split_tasks_normalizes_commas_and_newlines():
    result = split_tasks("Estudar, Lavar louça\nDormir , ")
    assert result == ["Estudar", "Lavar louça", "Dormir"]


def test_build_initial_tasks_assigns_ids():
    tasks = build_initial_tasks(["A", "B"])
    assert [task["id"] for task in tasks] == [1, 2]
    assert all(task["status"] == "pending" for task in tasks)


def test_select_completed_task_updates_state():
    tasks = build_initial_tasks(["A", "B"])
    completed_ids: list[int] = []
    selection = select_completed_task("2", tasks, completed_ids)
    assert selection == 2
    assert completed_ids == [2]
    assert tasks[1]["status"] == "completed"


def test_select_completed_task_rejects_invalid(monkeypatch):
    tasks = build_initial_tasks(["A"])
    with pytest.raises(ValueError):
        select_completed_task("", tasks, [])


def test_collect_new_tasks_handles_duplicates():
    tasks = build_initial_tasks(["A"])
    duplicate_notes: list[str] = []

    def confirm_keep(_item: str) -> bool:
        return False

    added = collect_new_tasks(["A", "B"], tasks, duplicate_notes, confirm_keep_fn=confirm_keep)
    assert added == ["B"]
    assert any("Duplicata" in note for note in duplicate_notes)
    assert len(tasks) == 2
