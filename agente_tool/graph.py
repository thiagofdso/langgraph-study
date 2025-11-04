"""Graph assembly for the agente_tool project."""

from __future__ import annotations

from functools import partial
from typing import Any, Callable

from langgraph.graph import END, StateGraph

from agente_tool.config import AppConfig, config as default_config
from agente_tool.state import GraphState
from agente_tool.utils import (
    STATUS_ERROR,
    execute_tools,
    finalize_response,
    format_response,
    invoke_model,
    plan_tool_usage,
    validate_input,
)
from agente_tool.utils.logging import get_logger
from agente_tool.utils.tools import calculator

logger = get_logger(__name__)


def _route_after_validation(state: GraphState) -> str:
    """Decide the next node after validation."""

    if state.get("status") == STATUS_ERROR:
        return "format_response"
    return "invoke_model"


def _route_after_invoke(state: GraphState) -> str:
    """Route after the initial model invocation."""

    if state.get("status") == STATUS_ERROR:
        return "format_response"
    return "plan_tool_usage"


def _route_after_planning(state: GraphState) -> str:
    """Choose the branch after planning."""

    plan = state.get("tool_plan")
    if plan:
        return "execute_tools"
    return "format_response"


def _route_after_tools(state: GraphState) -> str:
    """Handle branching after tool execution."""

    if state.get("status") == STATUS_ERROR:
        return "format_response"
    return "finalize_response"


def create_app(
    *,
    config: AppConfig | None = None,
    llm: Any | None = None,
    calculator_fn: Callable[[str], str] | None = None,
    checkpointer: Any | None = None,
):
    """Compile and return the agente_tool LangGraph workflow."""

    cfg = config or default_config
    calc_runner = calculator_fn or (
        lambda expression: calculator.invoke({"expression": expression})
    )

    graph = StateGraph(GraphState)
    graph.add_node("validate_input", validate_input)
    graph.add_node("invoke_model", partial(invoke_model, llm=llm, app_config=cfg))
    graph.add_node("plan_tool_usage", plan_tool_usage)
    graph.add_node("execute_tools", partial(execute_tools, calculator_fn=calc_runner))
    graph.add_node(
        "finalize_response", partial(finalize_response, llm=llm, app_config=cfg)
    )
    graph.add_node("format_response", format_response)

    graph.set_entry_point("validate_input")
    graph.add_conditional_edges("validate_input", _route_after_validation)
    graph.add_conditional_edges("invoke_model", _route_after_invoke)
    graph.add_conditional_edges("plan_tool_usage", _route_after_planning)
    graph.add_conditional_edges("execute_tools", _route_after_tools)
    graph.add_edge("finalize_response", "format_response")
    graph.add_edge("format_response", END)

    compiled = graph.compile(
        checkpointer=checkpointer or cfg.create_checkpointer(),
    )

    logger.debug("Grafo agente_tool compilado.")
    return compiled
