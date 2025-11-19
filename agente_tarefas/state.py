"""State schema and helpers for the task agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Dict, List, Literal, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TaskItem(TypedDict):
    id: int
    description: str
    status: Literal["pending", "completed"]
    source_round: Literal["round1", "round3"]


class TimelineEntry(TypedDict, total=False):
    round_id: Literal["round1", "round2", "round3"]
    user_input: str
    agent_response: str
    notes: str


class AgentState(TypedDict):
    """Graph state exchanged between nodes/CLI executions."""

    messages: Annotated[List[BaseMessage], add_messages]
    tasks: List[TaskItem]
    completed_ids: List[int]
    timeline: List[TimelineEntry]
    duplicate_notes: List[str]
    round_payload: Dict[str, object]


@dataclass(slots=True)
class StateFactory:
    """Factory helpers that produce AgentState dictionaries."""

    def build(self, *, messages: Sequence[BaseMessage]) -> AgentState:
        """Create a state object preloaded with the provided messages."""
        return {
            "messages": list(messages),
            "tasks": [],
            "completed_ids": [],
            "timeline": [],
            "duplicate_notes": [],
            "round_payload": {},
        }

    def empty(self) -> AgentState:
        """Return a blank state with no messages (useful for tests)."""

        return self.build(messages=[])


state_factory = StateFactory()

__all__ = ["AgentState", "TaskItem", "TimelineEntry", "state_factory"]
