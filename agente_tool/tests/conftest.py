"""Shared pytest fixtures for agente_tool."""

from __future__ import annotations

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
def create_app(default_config: AppConfig) -> Callable[..., Callable[[Dict], Dict]]:
    """Return a factory to build the LangGraph application with a stub LLM."""

    from agente_tool.graph import create_app as build_app

    def _factory(llm: DummyLLM | None = None):
        return build_app(config=default_config, llm=llm)

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
