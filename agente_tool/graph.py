"""Graph assembly for the agente_tool project."""

from __future__ import annotations

from functools import partial

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agente_tool.config import config
from agente_tool.state import GraphState
from agente_tool.utils import (
    STATUS_ERROR,
    format_response,
    handle_tool_result,
    invoke_model,
    plan_tool_usage,
    validate_input,
)
from agente_tool.utils.logging import get_logger
from agente_tool.utils.tools import calculator

logger = get_logger(__name__)


def _route_after_validation(state: GraphState) -> str:
    return "format_response" if state.get("status") == STATUS_ERROR else "invoke_model"


def _route_after_invoke(state: GraphState) -> str:
    return "format_response" if state.get("status") == STATUS_ERROR else "plan_tool_usage"


def _route_after_planning(state: GraphState) -> str:
    if state.get("status") == STATUS_ERROR:
        return "format_response"
    return "tools" if state.get("tool_plan") else "format_response"


def _route_after_tools(state: GraphState) -> str:
    return "format_response" if state.get("status") == STATUS_ERROR else "invoke_model"


def create_app():
    """Compile and return the agente_tool LangGraph workflow."""

    tools = [calculator]
    model = config.create_model_with_tools(tools)

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input)
    builder.add_node("invoke_model", partial(invoke_model, llm=model, app_config=config))
    builder.add_node("plan_tool_usage", plan_tool_usage)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("handle_tool_result", handle_tool_result)
    builder.add_node("format_response", format_response)

    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges("validate_input", _route_after_validation)
    builder.add_conditional_edges("invoke_model", _route_after_invoke)
    builder.add_conditional_edges("plan_tool_usage", _route_after_planning)
    builder.add_edge("tools", "handle_tool_result")
    builder.add_conditional_edges("handle_tool_result", _route_after_tools)
    builder.add_edge("format_response", END)

    compiled = builder.compile(checkpointer=config.create_checkpointer())
    logger.debug("Grafo agente_tool compilado.")
    return compiled


app = create_app()
