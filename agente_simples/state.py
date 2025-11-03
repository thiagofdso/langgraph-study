"""Shared state and input validation for the simple agent."""
from __future__ import annotations

from typing import Annotated, Any, Dict, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator
from typing_extensions import TypedDict


class DialogueInput(BaseModel):
    """Validated representation of the CLI question payload."""

    pergunta: str = Field(..., min_length=5, description="Pergunta em português")

    @field_validator("pergunta")
    @classmethod
    def _normalize_question(cls, value: str) -> str:
        """Trim whitespace and enforce minimum length for the provided question."""
        normalized = value.strip()
        if len(normalized) < 5:
            raise ValueError("Forneça uma pergunta com pelo menos 5 caracteres")
        return normalized

    def as_message(self) -> Dict[str, str]:
        """Return the normalized question formatted as a LangChain user message."""

        return {"role": "user", "content": self.pergunta}


class GraphState(TypedDict, total=False):
    """LangGraph shared state contract for the simple agent."""

    messages: Annotated[List[BaseMessage], add_messages]
    metadata: Dict[str, Any]
    status: str
    resposta: str
    error: str
    locale: str
    duration_seconds: float


DEFAULT_STATUS_PENDING = "pending"
DEFAULT_STATUS_VALIDATED = "validated"
DEFAULT_STATUS_RESPONDED = "responded"
DEFAULT_STATUS_COMPLETED = "completed"
DEFAULT_STATUS_ERROR = "error"
