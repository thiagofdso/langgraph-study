
"""LangGraph workflow definition for the memory agent."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agente_memoria.config import config
from agente_memoria.state import GraphState
from agente_memoria.utils.nodes import (
    format_response_node,
    invoke_model_node,
    load_history_node,
    update_memory_node,
    validate_question_node,
)


def create_app(checkpointer=None):
    """Create the compiled LangGraph app for the memory agent."""

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_question_node)
    builder.add_node("load_history", load_history_node)
    builder.add_node("invoke_model", invoke_model_node)
    builder.add_node("update_memory", update_memory_node)
    builder.add_node("format_response", format_response_node)

    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "load_history")
    builder.add_edge("load_history", "invoke_model")
    builder.add_edge("invoke_model", "update_memory")
    builder.add_edge("update_memory", "format_response")
    builder.add_edge("format_response", END)

    if checkpointer is None:
        checkpointer = config.create_checkpointer()
    return builder.compile(checkpointer=checkpointer)



