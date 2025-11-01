"""Test fixtures for the memory agent."""
from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, BaseMessage
from typing import List

class DummyLLM:
    def __init__(self, response: str):
        self._response = response

    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """Return a static result mimicking an LLM response."""
        return AIMessage(content=self._response)

@pytest.fixture
def mock_llm():
    """Fixture to mock the ChatGoogleGenerativeAI class."""
    return DummyLLM("Mocked response")