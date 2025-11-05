"""Typed state definitions for the agente_web LangGraph workflow."""

from __future__ import annotations

from typing import Any

from typing_extensions import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class GraphState(TypedDict, total=False):
    """Canonical state representation shared across graph nodes."""

    question: str
    metadata: dict[str, Any]
    messages: Annotated[list[BaseMessage], add_messages]
    search_results: list[dict[str, Any]]
    summary: str
    warnings: list[str]
    status: str

