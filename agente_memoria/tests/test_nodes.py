
"""Unit tests for the memory agent nodes."""
from __future__ import annotations

from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage

from agente_memoria.state import GraphState
from agente_memoria.utils.nodes import (
    format_response_node,
    invoke_model_node,
    validate_question_node,
)


def test_validate_question_node():
    """Verify that the validation node correctly processes valid and invalid inputs."""
    # Test with a valid question
    state = GraphState(messages=[HumanMessage(content="Hello")])
    result = validate_question_node(state)
    assert result["status"] == "validated"
    assert result["metadata"]["question"] == "Hello"

    # Test with an invalid (short) question
    state = GraphState(messages=[HumanMessage(content="Hi")])
    result = validate_question_node(state)
    assert result["status"] == "error"


@patch("agente_memoria.utils.nodes.config")
def test_invoke_model_node(mock_config, mock_llm):
    """Ensure the model invocation node calls the LLM and returns the response."""
    mock_config.create_llm.return_value = mock_llm
    state = GraphState(messages=[HumanMessage(content="Hello")])
    result = invoke_model_node(state)
    assert result["status"] == "responded"
    assert result["messages"][0].content == "Mocked response"


@patch("time.time", side_effect=[1, 2])
def test_format_response_node(mock_time):
    """Check that the response formatting node correctly calculates duration and formats the output."""
    state = GraphState(
        messages=[AIMessage(content="Mocked response")],
        metadata={"started_at": 1},
    )
    result = format_response_node(state)
    assert result["status"] == "completed"
    assert "Agent response: Mocked response" in result["resposta"]
    assert result["duration_seconds"] == 1
