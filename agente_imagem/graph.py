"""LangGraph workflow assembly for the imagem agent refactor."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agente_imagem.state import GraphState
from agente_imagem.utils import (
    format_response_node,
    invoke_model_node,
    prepare_image_node,
    validate_input_node,
)


def create_app():
    """Compile the LangGraph workflow for the image analysis agent."""

    builder = StateGraph(GraphState)
    builder.add_node("validate_input", validate_input_node)
    builder.add_node("prepare_image", prepare_image_node)
    builder.add_node("invoke_model", invoke_model_node)
    builder.add_node("format_response", format_response_node)
    builder.add_edge(START, "validate_input")
    builder.add_edge("validate_input", "prepare_image")
    builder.add_edge("prepare_image", "invoke_model")
    builder.add_edge("invoke_model", "format_response")
    builder.add_edge("format_response", END)
    return builder.compile()


app = create_app()
