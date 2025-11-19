"""LangGraph application for agente_tarefas."""
from __future__ import annotations

from typing import Any, Optional

from langgraph.graph import END, StateGraph

from agente_tarefas.config import AppConfig, settings
from agente_tarefas.state import AgentState
from agente_tarefas.utils.nodes import build_agent_node


def _resolve_config(config: Any = None) -> AppConfig:
    if config and hasattr(config, "create_llm") and hasattr(config, "create_checkpointer"):
        return config  # type: ignore[return-value]
    return settings


def create_graph(config: Optional[Any] = None):
    """Build and compile the single-node workflow for the agent."""

    app_config = _resolve_config(config)
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", build_agent_node(app_config))
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)

    # Placeholder for future middleware integration if needed.
    return workflow.compile(checkpointer=app_config.create_checkpointer())
__all__ = ["create_graph"]
