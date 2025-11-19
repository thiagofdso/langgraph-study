"""LangGraph application for agente_tarefas."""
from __future__ import annotations

from typing import Any, Optional

from langgraph.graph import END, StateGraph

from agente_tarefas.state import AgentState
from agente_tarefas.utils.nodes import (
    build_append_tasks_node,
    build_complete_task_node,
    build_prepare_round1_node,
    resolve_app_config,
)


def _register_round_nodes(workflow: StateGraph, app_config):
    """Add the round-processing nodes to the workflow."""

    workflow.add_node("prepare_round1", build_prepare_round1_node(app_config))
    workflow.add_node("complete_task", build_complete_task_node(app_config))
    workflow.add_node("append_tasks", build_append_tasks_node(app_config))

    workflow.set_entry_point("prepare_round1")
    workflow.add_edge("prepare_round1", "complete_task")
    workflow.add_edge("complete_task", "append_tasks")
    workflow.add_edge("append_tasks", END)


def create_graph(config: Optional[Any] = None):
    """Build and compile the workflow for the agent (multi-node ready)."""

    app_config = resolve_app_config(config)
    workflow = StateGraph(AgentState)
    _register_round_nodes(workflow, app_config)

    # Placeholder for future middleware integration if needed.
    return workflow.compile(checkpointer=app_config.create_checkpointer())
__all__ = ["create_graph"]
