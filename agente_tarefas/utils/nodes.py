"""LangGraph nodes used by agente_tarefas."""
from __future__ import annotations

from typing import Callable, Dict

from agente_tarefas.config import AppConfig, settings
from agente_tarefas.state import AgentState

NodeCallable = Callable[[AgentState], Dict[str, object]]


def build_agent_node(config: AppConfig | None = None) -> NodeCallable:
    """Return the single-node workflow used by the agent."""

    if config and hasattr(config, "create_llm"):
        app_config = config
    else:
        app_config = settings
    model = app_config.create_llm()

    def _agent_node(state: AgentState):
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    return _agent_node


__all__ = ["build_agent_node", "NodeCallable"]
