"""Shared state definitions and reducers for agente_mcp."""
from __future__ import annotations

from typing import Annotated, Any, Dict, Iterable, List, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

MAX_RUN_LOG_ENTRIES = 200
MAX_ERROR_ENTRIES = 50


class RunLogEntry(TypedDict, total=False):
    """Structured payload describing a single tool execution or phase event."""

    phase: str
    tool_name: str
    status: str
    duration_ms: int
    message: str


class ErrorEntry(TypedDict, total=False):
    """Structured payload capturing recoverable errors during the run."""

    category: str
    message: str
    details: Dict[str, Any]


def _bounded_extend(
    existing: List[Dict[str, Any]] | None,
    new_entries: Iterable[Dict[str, Any]] | None,
    *,
    limit: int,
) -> List[Dict[str, Any]]:
    """Return concatenated entries without exceeding the configured limit."""

    combined: List[Dict[str, Any]] = list(existing or [])
    if new_entries:
        for entry in new_entries:
            if entry:
                combined.append(entry)
    if len(combined) > limit:
        combined = combined[-limit:]
    return combined


def add_run_log(
    existing: List[RunLogEntry] | None, new_entries: Iterable[RunLogEntry] | None
) -> List[RunLogEntry]:
    """Reducer used by LangGraph to accumulate run_log entries."""

    return _bounded_extend(existing, new_entries, limit=MAX_RUN_LOG_ENTRIES)


def add_error_entries(
    existing: List[ErrorEntry] | None, new_entries: Iterable[ErrorEntry] | None
) -> List[ErrorEntry]:
    """Reducer used by LangGraph to accumulate error entries."""

    return _bounded_extend(existing, new_entries, limit=MAX_ERROR_ENTRIES)


def merge_metadata(
    existing: Dict[str, Any] | None, additional: Dict[str, Any] | None
) -> Dict[str, Any]:
    """Reducer that merges metadata dictionaries, preferring the newest values."""

    merged: Dict[str, Any] = dict(existing or {})
    if additional:
        merged.update(additional)
    return merged


class AgentSession(TypedDict, total=False):
    """LangGraph state contract for agente_mcp sessions."""

    thread_id: str
    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Annotated[Dict[str, Any], merge_metadata]
    run_log: Annotated[List[RunLogEntry], add_run_log]
    errors: Annotated[List[ErrorEntry], add_error_entries]
    status: str


def bootstrap_session(
    *,
    thread_id: str,
    user_messages: Sequence[str],
    system_prompt: str,
    metadata: Dict[str, Any] | None = None,
) -> AgentSession:
    """Create an AgentSession populated with the standard system + user messages."""

    trimmed_prompt = system_prompt.strip()
    if not trimmed_prompt:
        raise ValueError("system_prompt não pode estar vazio")

    messages: List[BaseMessage] = [SystemMessage(content=trimmed_prompt)]
    human_messages = [text.strip() for text in user_messages if text.strip()]
    if not human_messages:
        raise ValueError("Forneça ao menos uma mensagem do usuário para iniciar a sessão")
    messages.extend(HumanMessage(content=content) for content in human_messages)

    session: AgentSession = {
        "thread_id": thread_id.strip() or "manual-run",
        "messages": messages,
        "metadata": metadata or {},
        "run_log": [],
        "errors": [],
        "status": "initialized",
    }
    return session


__all__ = [
    "AgentSession",
    "RunLogEntry",
    "ErrorEntry",
    "add_error_entries",
    "add_run_log",
    "bootstrap_session",
    "merge_metadata",
]
