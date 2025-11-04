"""Shared pytest fixtures for agente_tool."""

from __future__ import annotations

import types
from typing import Callable, Dict, Iterable, List, Union

import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from agente_tool.config import AppConfig
from agente_tool.state import GraphState, ThreadConfig


class DummyLLM:
    """Simple Gemini stand-in returning a static message."""

    ResponseType = Union[str, AIMessage, Dict[str, object]]

    def __init__(self, responses: Iterable[ResponseType] | ResponseType):
        if isinstance(responses, (str, AIMessage, dict)):
            self._responses: List[DummyLLM.ResponseType] = [responses]  # type: ignore[list-item]
        else:
            self._responses = list(responses)
        self._cursor = 0
        self._tools: List[object] = []

    def bind_tools(self, tools):  # pragma: no cover - comportamento simples de stub
        self._tools = list(tools)
        return self

    def invoke(
        self, messages: List[BaseMessage]
    ) -> AIMessage:  # pragma: no cover - exercised indirectly
        """Return the next pre-captured response."""

        if self._cursor >= len(self._responses):
            content = self._responses[-1] if self._responses else ""
        else:
            content = self._responses[self._cursor]
            self._cursor += 1
        if isinstance(content, AIMessage):
            return content
        if isinstance(content, dict):
            return AIMessage(**content)
        return AIMessage(content=str(content))


@pytest.fixture(scope="session")
def default_config() -> AppConfig:
    """Provide an AppConfig instance wired to a fake API key for tests."""

    return AppConfig(api_key="fake-test-key")


@pytest.fixture()
def thread_config(default_config: AppConfig) -> ThreadConfig:
    """Return a thread configuration using the default thread id."""

    return ThreadConfig(thread_id=default_config.default_thread_id)


@pytest.fixture()
def create_app(default_config: AppConfig, monkeypatch) -> Callable[..., Callable[[Dict], Dict]]:
    """Return a factory to build the LangGraph application with a stub LLM."""

    from agente_tool import config as config_module
    from agente_tool.graph import create_app as build_app

    def _factory(llm: DummyLLM | None = None):
        if llm is None:
            llm_instance = DummyLLM("Stub response")
        else:
            llm_instance = llm

        original_config = config_module.config
        original_create = default_config.create_model_with_tools

        def fake_create(self, tools):
            return llm_instance.bind_tools(tools)

        config_module.config = default_config
        default_config.create_model_with_tools = types.MethodType(fake_create, default_config)

        try:
            return build_app()
        finally:
            default_config.create_model_with_tools = original_create  # type: ignore[assignment]
            config_module.config = original_config

    return _factory


@pytest.fixture()
def initial_state() -> GraphState:
    """Build an initial sample state used across tests."""

    state: GraphState = {
        "messages": [HumanMessage(content="quanto é 300 dividido por 4?")],
        "metadata": {},
        "status": "pending",
    }
    return state
