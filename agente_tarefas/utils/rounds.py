"""Input parsing and validation utilities for the CLI rounds."""
from __future__ import annotations

from typing import Callable, List, Sequence

from agente_tarefas.state import TaskItem

ConfirmationFunc = Callable[[str], bool]


def split_tasks(raw: str) -> List[str]:
    """Split comma/newline-separated tasks into sanitized fragments."""

    fragments = [segment.strip() for segment in raw.replace("\n", ",").split(",")]
    return [fragment for fragment in fragments if fragment]


def build_initial_tasks(raw_items: Sequence[str]) -> List[TaskItem]:
    """Create TaskItem entries from user-provided strings."""

    return [
        {
            "id": index + 1,
            "description": item,
            "status": "pending",
            "source_round": "round1",
        }
        for index, item in enumerate(raw_items)
    ]


def select_completed_task(selection_raw: str, tasks_state: List[TaskItem], completed_ids: List[int]) -> int:
    """Validate the numeric selection and update the task status."""

    if not selection_raw:
        raise ValueError("Informe um número válido para continuar.")
    if not selection_raw.isdigit():
        raise ValueError("Utilize apenas números correspondentes à lista apresentada.")

    selection = int(selection_raw)
    if selection < 1 or selection > len(tasks_state):
        raise ValueError("Esse número não está na lista. Tente novamente.")
    if selection in completed_ids:
        raise ValueError("Essa tarefa já foi concluída anteriormente. Escolha outra.")

    for task in tasks_state:
        if task["id"] == selection:
            task["status"] = "completed"
            break
    completed_ids.append(selection)
    return selection


def collect_new_tasks(
    entries: Sequence[str],
    tasks_state: List[TaskItem],
    duplicate_notes: List[str],
    *,
    confirm_keep_fn: ConfirmationFunc,
) -> List[str]:
    """Insert new tasks, handling duplicates via a confirmation callback."""

    existing_descriptions = {task["description"].casefold() for task in tasks_state}
    next_id = len(tasks_state) + 1
    added_descriptions: List[str] = []

    for item in entries:
        lowered = item.casefold()
        if lowered in existing_descriptions:
            keep = confirm_keep_fn(item)
            decision = "mantida" if keep else "ignorada"
            duplicate_notes.append(f"Duplicata '{item}' foi {decision} pelo usuário")
            if not keep:
                continue
        tasks_state.append(
            {
                "id": next_id,
                "description": item,
                "status": "pending",
                "source_round": "round3",
            }
        )
        existing_descriptions.add(lowered)
        added_descriptions.append(item)
        next_id += 1

    return added_descriptions


__all__ = [
    "ConfirmationFunc",
    "split_tasks",
    "build_initial_tasks",
    "select_completed_task",
    "collect_new_tasks",
]
