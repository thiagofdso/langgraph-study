"""State schema and helpers for the dynamic task agent."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, List, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from agente_tarefas.utils.operations import Operation


class OperationReport(TypedDict, total=False):
    """Summaries about the operations executed in the current turn."""

    added: List[str]
    removed: List[str]
    missing: List[str]
    requested_listing: bool
    listing_only: bool
    log_entry: str


class OperationError(TypedDict, total=False):
    """Structured error returned when the JSON operation payload is invalid."""

    code: str
    message: str
    details: str


class AgentState(TypedDict, total=False):
    """Graph state exchanged between LangGraph CLI turns."""

    messages: Annotated[List[BaseMessage], add_messages]
    tasks: List[str]
    operations: List[Operation]
    operation_report: OperationReport
    error: OperationError


@dataclass(slots=True)
class StateFactory:
    """Factory helpers that produce AgentState dictionaries."""

    def build(self, *, messages: Sequence[BaseMessage]) -> AgentState:
        """Create a state object preloaded with the provided messages."""

        return {
            "messages": list(messages),
            "tasks": [],
            "operations": [],
            "operation_report": {},
            "error": {},
        }

    def empty(self) -> AgentState:
        """Return a blank state with no messages (useful for tests)."""

        return self.build(messages=[])


state_factory = StateFactory()

__all__ = ["AgentState", "OperationReport", "OperationError", "state_factory"]
