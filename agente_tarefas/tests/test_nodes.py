"""Unit tests for agente_tarefas graph nodes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agente_tarefas.state import AgentState, state_factory
from agente_tarefas.utils.nodes import (
    build_append_tasks_node,
    build_complete_task_node,
    build_prepare_round1_node,
    resolve_app_config,
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

    def create_checkpointer(self):  # pragma: no cover - not used in unit tests
        class _DummyCheckpointer:
            def put(self, *args, **kwargs):
                return None

        return _DummyCheckpointer()


@pytest.fixture()
def fake_config() -> _FakeConfig:
    return _FakeConfig(responses=["round1", "round2", "round3"])


@pytest.fixture()
def base_state() -> AgentState:
    return state_factory.build(messages=[SystemMessage(content="sys")])


def test_prepare_round1_node_populates_tasks(base_state: AgentState, fake_config: _FakeConfig):
    node = build_prepare_round1_node(fake_config)
    base_state["round_payload"] = {
        "round": "round1",
        "user_input": "Estudar, Lavar louça",
        "raw_tasks": "Estudar, Lavar louça",
        "tasks_list": ["Estudar", "Lavar louça"],
    }

    result = node(base_state)

    assert [task["description"] for task in result["tasks"]] == ["Estudar", "Lavar louça"]
    assert result["completed_ids"] == []
    assert result["duplicate_notes"] == []
    assert result["round_payload"] == {}
    assert result["timeline"][0]["round_id"] == "round1"
    assert result["messages"][-1].content == "round1"


def test_complete_task_node_updates_status(fake_config: _FakeConfig):
    state: AgentState = state_factory.build(messages=[SystemMessage(content="sys")])
    state["messages"].extend([
        HumanMessage(content="R1"),
        AIMessage(content="Ok"),
    ])
    state["tasks"] = [
        {"id": 1, "description": "Estudar", "status": "pending", "source_round": "round1"},
        {"id": 2, "description": "Correr", "status": "pending", "source_round": "round1"},
    ]
    state["round_payload"] = {"round": "round2", "user_input": "1", "selected_id": 1}

    node = build_complete_task_node(fake_config)
    result = node(state)

    assert result["completed_ids"] == [1]
    assert result["tasks"][0]["status"] == "completed"
    assert result["messages"][-1].content == "round1"
    assert result["timeline"][-1]["user_input"] == "1"


def test_append_tasks_node_respects_duplicate_decisions(fake_config: _FakeConfig):
    state: AgentState = state_factory.build(messages=[SystemMessage(content="sys")])
    state["tasks"] = [
        {"id": 1, "description": "Estudar", "status": "pending", "source_round": "round1"},
    ]
    state["duplicate_notes"] = []
    state["round_payload"] = {
        "round": "round3",
        "user_input": "Passear, Estudar",
        "entries": ["Passear", "Estudar"],
        "duplicate_decisions": [{"task": "Estudar", "keep": False}],
    }

    node = build_append_tasks_node(fake_config)
    result = node(state)

    assert [task["description"] for task in result["tasks"]] == ["Estudar", "Passear"]
    # duplicate decision false -> note registered, but task not duplicated
    assert "foi ignorada" in result["duplicate_notes"][0]
    assert result["messages"][-1].content == "round1"
    assert result["timeline"][-1]["round_id"] == "round3"
