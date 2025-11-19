"""LangGraph application for agente_tarefas."""
from __future__ import annotations

from typing import Any, Optional

from langgraph.graph import END, StateGraph

from agente_tarefas.state import AgentState
from agente_tarefas.utils.nodes import (
    build_apply_operations_node,
    build_parse_operations_node,
    build_summarize_node,
    resolve_app_config,
)


def create_graph(config: Optional[Any] = None):
    """Build and compile the workflow for the agent."""

    app_config = resolve_app_config(config)
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_operations", build_parse_operations_node(app_config))
    workflow.add_node("apply_operations", build_apply_operations_node())
    workflow.add_node("summarize", build_summarize_node())

    workflow.set_entry_point("parse_operations")
    workflow.add_edge("parse_operations", "apply_operations")
    workflow.add_edge("apply_operations", "summarize")
    workflow.add_edge("summarize", END)

    return workflow.compile(checkpointer=app_config.create_checkpointer())


__all__ = ["create_graph"]
