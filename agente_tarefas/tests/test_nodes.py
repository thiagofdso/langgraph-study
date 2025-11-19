"""Unit tests for dynamic agente_tarefas nodes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agente_tarefas.state import AgentState, state_factory
from agente_tarefas.utils.nodes import (
    build_apply_operations_node,
    build_parse_operations_node,
    build_summarize_node,
)


@dataclass
class _FakeConfig:
    responses: List[str]

    def __post_init__(self) -> None:
        self._cursor = 0

    def create_llm(self):
        config = self

        class _DummyLLM:
            def invoke(self_inner, messages):
                _ = messages
                response_text = config.responses[config._cursor]
                config._cursor = min(config._cursor + 1, len(config.responses) - 1)
                return AIMessage(content=response_text)

        return _DummyLLM()

    def create_checkpointer(self):  # pragma: no cover - not used in node tests
        raise NotImplementedError


@pytest.fixture()
def base_state() -> AgentState:
    return state_factory.build(messages=[HumanMessage(content="Adicione estudar e remover correr")])


def test_parse_operations_node_extracts_operations(base_state: AgentState):
    fake_config = _FakeConfig(
        responses=[
            """```json
            [
              {"op":"add","tasks":["estudar","fazer compras"]},
              {"op":"del","tasks":["correr"]},
              {"op":"listar"}
            ]
            ```"""
        ]
    )
    node = build_parse_operations_node(fake_config)

    result = node(base_state)

    assert result["error"] == {}
    assert result["operations"][0]["op"] == "add"
    assert result["operations"][1]["op"] == "del"
    assert result["operations"][2]["op"] == "listar"


def test_parse_operations_node_handles_invalid_json(base_state: AgentState):
    fake_config = _FakeConfig(responses=["isso não é json"])
    node = build_parse_operations_node(fake_config)

    result = node(base_state)

    assert result["operations"] == []
    assert result["error"]["code"] == "invalid-json"


def test_parse_operations_node_reports_missing_tasks(base_state: AgentState):
    fake_config = _FakeConfig(
        responses=[
            '[{"op":"add"}]'
        ]
    )
    node = build_parse_operations_node(fake_config)

    result = node(base_state)

    assert result["error"]["code"] == "missing-tasks"
    assert result["operations"] == []


def test_apply_operations_executes_add_and_delete():
    state: AgentState = state_factory.build(messages=[SystemMessage(content="sys")])
    state["tasks"] = ["Ler livro"]
    state["operations"] = [
        {"op": "add", "tasks": ["Estudar", "Fazer compras"]},
        {"op": "del", "tasks": ["ler livro", "Passear"]},
    ]
    state["error"] = {}

    node = build_apply_operations_node()
    result = node(state)

    assert sorted(result["tasks"]) == ["Estudar", "Fazer compras"]
    assert "Ler livro" in result["operation_report"]["removed"]
    assert "Passear" in result["operation_report"]["missing"]


def test_summarize_node_reports_errors():
    state: AgentState = state_factory.build(messages=[HumanMessage(content="Liste as tarefas")])
    state["tasks"] = ["Estudar"]
    state["operation_report"] = {"requested_listing": True}
    state["error"] = {"code": "invalid-json", "message": "json ruim"}

    node = build_summarize_node()
    result = node(state)

    final_message = result["messages"][-1]
    assert isinstance(final_message, AIMessage)
    assert "json" in final_message.content.lower()
    assert "- Estudar" in final_message.content


def test_listar_only_flow_leaves_state_intact():
    state: AgentState = state_factory.build(messages=[HumanMessage(content="Liste as tarefas")])
    state["tasks"] = ["Estudar", "Ler"]
    state["operations"] = [{"op": "listar"}]
    state["error"] = {}

    apply_node = build_apply_operations_node()
    updated_state = apply_node(state)
    assert updated_state["tasks"] == ["Estudar", "Ler"]
    assert updated_state["operation_report"]["listing_only"] is True

    summarize = build_summarize_node()
    summary_state = {
        **state,
        **updated_state,
        "messages": state["messages"],
    }
    final_state = summarize(summary_state)
    final_message = final_state["messages"][-1].content
    assert "apenas listar" in final_message.lower()
    assert "- Estudar" in final_message


def test_apply_operations_skips_when_error_present():
    state: AgentState = state_factory.build(messages=[HumanMessage(content="remova tudo")])
    state["tasks"] = ["Estudar"]
    state["operations"] = [{"op": "del", "tasks": ["Estudar"]}]
    state["error"] = {"code": "invalid-json", "message": "bad"}

    node = build_apply_operations_node()
    result = node(state)

    assert result["tasks"] == ["Estudar"]
    assert result["operation_report"]["removed"] == []
