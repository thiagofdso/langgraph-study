"""State models shared across agente_tool graph runs."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class ThreadConfig(BaseModel):
    """Execution configuration tied to a LangGraph thread."""

    thread_id: str = Field(
        ...,
        description="Identificador alfanumérico para reuso do checkpointer.",
        min_length=3,
        max_length=64,
        pattern="^[a-zA-Z0-9-_]+$",
    )


class GraphState(TypedDict, total=False):
    """State dictionary propagated between nodes."""

    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Dict[str, Any]
    status: str
    resposta: str
    selected_tool: Optional[str]
    tool_plan: Optional["ToolPlan"]
    tool_call: Optional[Dict[str, Any]]
    pending_tool_calls: Optional[List[Dict[str, Any]]]
    last_tool_run: Optional[Dict[str, Any]]
    duration_seconds: float


class ToolPlan(TypedDict, total=False):
    """Minimal representation of the plan for tool execution."""

    name: str
    args: Dict[str, Any]
    call_id: Optional[str]
