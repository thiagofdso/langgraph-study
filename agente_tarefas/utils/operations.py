"""Structured task operations and validation helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Literal, Sequence, TypedDict

OperationType = Literal["listar", "add", "del"]


class Operation(TypedDict, total=False):
    """Structured representation of an operation requested by the user."""

    op: OperationType
    tasks: List[str]


@dataclass(slots=True)
class OperationValidationError(ValueError):
    """Exception raised when an operation payload cannot be validated."""

    code: str
    message: str
    details: str | None = None

    def __str__(self) -> str:  # pragma: no cover - repr convenience
        detail_part = f" ({self.details})" if self.details else ""
        return f"{self.message}{detail_part}"


def normalize_task_name(raw: str) -> str:
    """Trim whitespace and collapse repeated spaces within a task name."""

    normalized = " ".join(raw.strip().split())
    if not normalized:
        raise OperationValidationError(
            code="empty-task",
            message="Os nomes das tarefas não podem ficar vazios depois da limpeza.",
        )
    return normalized


def _deduplicate_preserving_order(items: Sequence[str]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for item in items:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return ordered


def _validate_tasks_field(op: OperationType, payload: Any) -> List[str]:
    if op == "listar":
        return []

    if "tasks" not in payload:
        raise OperationValidationError(
            code="missing-tasks",
            message=f"A operação '{op}' exige o campo 'tasks' com ao menos um item.",
        )

    tasks_value = payload["tasks"]
    if not isinstance(tasks_value, Iterable) or isinstance(tasks_value, (str, bytes)):
        raise OperationValidationError(
            code="invalid-tasks",
            message="O campo 'tasks' deve ser uma lista de textos.",
        )

    cleaned = [_normalize_and_validate_task(item) for item in tasks_value]
    deduped = _deduplicate_preserving_order(cleaned)
    if not deduped:
        raise OperationValidationError(
            code="empty-tasks",
            message="Forneça pelo menos uma tarefa não vazia na operação.",
        )
    return deduped


def _normalize_and_validate_task(value: Any) -> str:
    if not isinstance(value, str):
        raise OperationValidationError(
            code="task-type",
            message="Cada tarefa deve ser uma string.",
        )
    return normalize_task_name(value)


def validate_operation(payload: Any) -> Operation:
    """Validate a single JSON operation into the canonical Operation structure."""

    if not isinstance(payload, dict):
        raise OperationValidationError(
            code="invalid-structure",
            message="Cada operação precisa ser um objeto JSON com o campo 'op'.",
            details=f"Tipo recebido: {type(payload).__name__}",
        )

    op_value = payload.get("op")
    if op_value not in ("listar", "add", "del"):
        raise OperationValidationError(
            code="invalid-op",
            message="Use apenas as operações 'listar', 'add' ou 'del'.",
        )

    tasks = _validate_tasks_field(op_value, payload)
    operation: Operation = {"op": op_value}  # type: ignore[assignment]
    if tasks:
        operation["tasks"] = tasks
    return operation


def validate_operations(raw_payload: Any) -> List[Operation]:
    """Validate a list of operations preserving the order returned by the LLM."""

    if not isinstance(raw_payload, list):
        raise OperationValidationError(
            code="invalid-root",
            message="Responda com um array JSON contendo as operações solicitadas.",
            details=f"Tipo recebido: {type(raw_payload).__name__}",
        )

    validated: List[Operation] = []
    for item in raw_payload:
        validated.append(validate_operation(item))
    return validated


__all__ = [
    "Operation",
    "OperationValidationError",
    "validate_operation",
    "validate_operations",
    "normalize_task_name",
]
