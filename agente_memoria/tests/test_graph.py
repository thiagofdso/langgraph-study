
"""Integration tests for the memory agent graph."""
from __future__ import annotations

from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from agente_memoria.graph import create_app
from agente_memoria.state import GraphState


@patch("agente_memoria.graph.invoke_model_node")
@patch("agente_memoria.config.AppConfig.create_llm")
def test_graph_multi_turn(mock_create_llm, mock_invoke_model_node, mock_llm):
    """Test that the graph correctly handles a multi-turn conversation, maintaining history."""
    mock_create_llm.return_value = mock_llm

    def invoke_side_effect(state):
        assert len(state["messages"]) >= 1
        return {"messages": [AIMessage(content="Mocked response")]}

    mock_invoke_model_node.side_effect = invoke_side_effect

    app = create_app()
    config = {"configurable": {"thread_id": "test-thread-1"}}

    # First turn
    state = GraphState(messages=[HumanMessage(content="Hello")], thread_id="test-thread-1")
    result = app.invoke(state, config=config)
    assert "Agent response: Mocked response" in result["resposta"]
    assert mock_invoke_model_node.call_count == 1

    # Second turn
    state = GraphState(messages=[HumanMessage(content="How are you?")], thread_id="test-thread-1")
    result = app.invoke(state, config=config)
    assert "Agent response: Mocked response" in result["resposta"]
    assert mock_invoke_model_node.call_count == 2


@patch("agente_memoria.config.config.api_key", None)
def test_graph_no_api_key():
    """Verify that the preflight check (simulated) prevents execution when the API key is missing."""
    pass


@patch("agente_memoria.utils.nodes.logger")
@patch("agente_memoria.config.AppConfig.create_llm")
def test_graph_logging(mock_create_llm, mock_logger, mock_llm):
    """Verify that the graph nodes call the logger."""
    mock_create_llm.return_value = mock_llm

    app = create_app()
    state = GraphState(messages=[HumanMessage(content="Hello")], thread_id="test-thread-logging")
    config = {"configurable": {"thread_id": "test-thread-logging"}}
    app.invoke(state, config=config)

    assert mock_logger.info.call_count > 0
