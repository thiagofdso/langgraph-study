"""Shared LangGraph state definitions for agente_perguntas."""

from __future__ import annotations

from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """State carried across the graph nodes for each interaction."""

    messages: Annotated[list[BaseMessage], add_messages]
    answer: str
    confidence: float
    status: Literal["respondido automaticamente", "encaminhar para humano"]
    notes: str


__all__ = ["AgentState"]
