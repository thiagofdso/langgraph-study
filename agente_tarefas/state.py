"""State schema and helpers for the task agent."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, List, Literal, Sequence, TypedDict

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
    messages: Annotated[List[BaseMessage], add_messages]
    tasks: List[TaskItem]
    completed_ids: List[int]
    timeline: List[TimelineEntry]


@dataclass(slots=True)
class StateFactory:
    """Create default state payloads for graph executions."""

    def build(self, *, messages: Sequence[BaseMessage]) -> AgentState:
        return {
            "messages": list(messages),
            "tasks": [],
            "completed_ids": [],
            "timeline": [],
        }


state_factory = StateFactory()

__all__ = ["AgentState", "TaskItem", "TimelineEntry", "state_factory"]
