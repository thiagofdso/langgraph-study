"""LangGraph workflow definition for the simple agent."""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agente_simples.state import GraphState
from agente_simples.utils import (
    format_answer_node,
    invoke_model_node,
    validate_question_node,
)


def create_app():
    """Create the compiled LangGraph app for the simple agent."""

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_question_node)
    builder.add_node("invoke_model", invoke_model_node)
    builder.add_node("format_response", format_answer_node)

    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "invoke_model")
    builder.add_edge("invoke_model", "format_response")
    builder.add_edge("format_response", END)

    return builder.compile()


app = create_app()
