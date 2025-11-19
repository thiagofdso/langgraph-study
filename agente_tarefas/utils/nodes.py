"""LangGraph nodes for the dynamic task agent."""
from __future__ import annotations

import json
from typing import Dict, List, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from agente_tarefas.config import AppConfig, settings
from agente_tarefas.state import AgentState, OperationError, OperationReport
from agente_tarefas.utils.logging import build_operation_log
from agente_tarefas.utils.operations import (
    Operation,
    OperationValidationError,
    normalize_task_name,
    validate_operations,
)
from agente_tarefas.utils.prompts import SYSTEM_PROMPT, build_operations_prompt


def resolve_app_config(config: AppConfig | None = None) -> AppConfig:
    """Return a usable AppConfig for node construction."""

    if config and hasattr(config, "create_llm") and hasattr(config, "create_checkpointer"):
        return config
    return settings


def _ensure_system_prompt(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    if messages and isinstance(messages[0], SystemMessage):
        return list(messages)
    return [SystemMessage(content=SYSTEM_PROMPT), *messages]


def _last_user_message(messages: Sequence[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message.content
    return ""


def _strip_json_block(content: str) -> str:
    text = content.strip()
    if text.startswith("```"):
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return text


def _build_error(code: str, message: str, details: str | None = None) -> OperationError:
    error: OperationError = {"code": code, "message": message}
    if details:
        error["details"] = details
    return error


def build_parse_operations_node(config: AppConfig | None = None):
    """Create a node that asks the LLM for structured operations."""

    app_config = resolve_app_config(config)

    def _node(state: AgentState) -> Dict[str, object]:
        current_messages = state.get("messages", [])
        user_message = _last_user_message(current_messages)
        if not user_message:
            # Nothing to do if no new message was supplied.
            return {}

        messages = _ensure_system_prompt(current_messages)
        prompt = build_operations_prompt(state.get("tasks", []), user_message)

        prompt_message = HumanMessage(content=prompt)
        model = app_config.create_llm()
        response = model.invoke([*messages, prompt_message])
        messages = [*messages, prompt_message, response]

        cleaned = _strip_json_block(response.content)
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            error = _build_error(
                "invalid-json",
                "Não consegui interpretar as operações em JSON. Revise o formato e tente novamente.",
                details=str(exc),
            )
            return {"messages": messages, "operations": [], "error": error}

        try:
            operations = validate_operations(payload)
        except OperationValidationError as exc:
            error = _build_error(exc.code, exc.message, exc.details)
            return {"messages": messages, "operations": [], "error": error}

        return {"messages": messages, "operations": operations, "error": {}}

    return _node


def build_apply_operations_node():
    """Create a node that mutates the in-memory task list."""

    def _node(state: AgentState) -> Dict[str, object]:
        tasks = list(state.get("tasks", []))
        operations = state.get("operations", [])
        error = state.get("error", {})

        has_listing = any(op.get("op") == "listar" for op in operations)
        listing_only = bool(operations) and all(op.get("op") == "listar" for op in operations)
        report: OperationReport = {
            "added": [],
            "removed": [],
            "missing": [],
            "requested_listing": has_listing,
            "listing_only": listing_only,
        }

        if error and error.get("code"):
            # Preserve error information for the summarizer.
            report["log_entry"] = build_operation_log(report, error)
            return {
                "tasks": tasks,
                "operation_report": report,
            }

        if listing_only:
            report["log_entry"] = build_operation_log(report, {})
            return {
                "tasks": tasks,
                "operations": [],
                "operation_report": report,
                "error": {},
            }

        for operation in operations:
            op_type = operation["op"]
            if op_type == "listar":
                continue
            if op_type == "add":
                _apply_add(operation, tasks, report)
            elif op_type == "del":
                _apply_del(operation, tasks, report)

        report["log_entry"] = build_operation_log(report, {})
        return {
            "tasks": tasks,
            "operations": [],
            "operation_report": report,
            "error": {},
        }

    return _node


def _apply_add(operation: Operation, tasks: List[str], report: OperationReport) -> None:
    entries = operation.get("tasks", [])
    existing = {item.casefold() for item in tasks}
    for entry in entries:
        normalized = normalize_task_name(entry)
        key = normalized.casefold()
        if key in existing:
            continue
        tasks.append(normalized)
        existing.add(key)
        report.setdefault("added", []).append(normalized)


def _apply_del(operation: Operation, tasks: List[str], report: OperationReport) -> None:
    entries = operation.get("tasks", [])
    remaining: List[str] = []
    removed: List[str] = report.setdefault("removed", [])
    missing: List[str] = report.setdefault("missing", [])

    targets = {normalize_task_name(item).casefold(): normalize_task_name(item) for item in entries}
    seen_keys: set[str] = set()

    for task in tasks:
        key = task.casefold()
        if key in targets and key not in seen_keys:
            removed.append(task)
            seen_keys.add(key)
            continue
        remaining.append(task)

    for target_key, rendered in targets.items():
        if target_key not in seen_keys:
            missing.append(rendered)

    tasks[:] = remaining


def build_summarize_node():
    """Create a node that summarizes the outcome to the user."""

    def _node(state: AgentState) -> Dict[str, object]:
        messages = _ensure_system_prompt(state.get("messages", []))
        tasks = state.get("tasks", [])
        report = state.get("operation_report", {})
        error = state.get("error", {})

        summary = _build_summary_text(tasks, report, error)
        messages.append(AIMessage(content=summary))

        return {
            "messages": messages,
            "operations": [],
            "operation_report": {},
            "error": {},
        }

    return _node


def _build_summary_text(tasks: Sequence[str], report: OperationReport, error: OperationError) -> str:
    header_lines: List[str] = []
    if error and error.get("code"):
        header_lines.append("Não consegui interpretar suas instruções sem ambiguidade.")
        header_lines.append(f"Motivo: {error.get('message', 'formato inválido')}.")
        details = error.get("details")
        if details:
            header_lines.append(f"Detalhes técnicos: {details}")
        header_lines.append(
            "Use o formato JSON exatamente como: "
            '[{"op":"add","tasks":["estudar"]},{"op":"del","tasks":["ler"]}] ou [{"op":"listar"}].'
        )
        header_lines.append("Nenhuma alteração foi aplicada; abaixo está a lista atual.")
    else:
        additions = report.get("added") or []
        deletions = report.get("removed") or []
        missing = report.get("missing") or []
        requested_listing = report.get("requested_listing")
        listing_only = report.get("listing_only")

        if listing_only:
            header_lines.append("Você solicitou apenas listar as tarefas; nenhuma alteração foi aplicada.")
        if additions:
            header_lines.append(f"Tarefas adicionadas: {', '.join(additions)}.")
        if deletions:
            header_lines.append(f"Tarefas removidas: {', '.join(deletions)}.")
        if missing:
            header_lines.append(f"Não encontrei: {', '.join(missing)} (já estavam ausentes).")
        if not additions and not deletions and requested_listing and not missing and not listing_only:
            header_lines.append("Você solicitou apenas listar as tarefas; nada foi alterado.")
        if not header_lines:
            header_lines.append("Nenhuma alteração foi aplicada, mas sua solicitação foi registrada.")

    rendered_tasks = "\n".join(f"- {task}" for task in tasks) if tasks else "- (nenhuma tarefa registrada)"
    header_lines.append("\nLista atual:")
    header_lines.append(rendered_tasks)
    return "\n".join(header_lines)


__all__ = [
    "build_parse_operations_node",
    "build_apply_operations_node",
    "build_summarize_node",
    "resolve_app_config",
]
