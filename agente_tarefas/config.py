"""Configuration helpers for the task agent."""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

AGENT_ROOT = Path(__file__).resolve().parent
load_dotenv(AGENT_ROOT / ".env")


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing or invalid."""


@dataclass(slots=True)
class AppConfig:
    """Centralized configuration and helpers for the task agent."""

    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    thread_prefix: str = os.getenv("AGENT_THREAD_PREFIX", "agente-tarefas")

    def create_llm(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini chat model with validation."""

        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY não encontrado. Configure agente_tarefas/.env antes de executar."
            )
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )

    def create_checkpointer(self) -> InMemorySaver:
        """Factory for the default in-memory checkpointer."""

        return InMemorySaver()

    def build_thread_id(self) -> str:
        """Generate a unique identifier for a CLI session."""

        return f"{self.thread_prefix}-{uuid.uuid4()}"


def preflight_config_check() -> List[Dict[str, str]]:
    """Return diagnostic checks for required configuration entries."""

    results: List[Dict[str, str]] = []

    if os.getenv("GEMINI_API_KEY"):
        results.append(
            {
                "name": "GEMINI_API_KEY",
                "result": "pass",
                "message": "Chave encontrada.",
            }
        )
    else:
        results.append(
            {
                "name": "GEMINI_API_KEY",
                "result": "fail",
                "message": "Defina GEMINI_API_KEY em agente_tarefas/.env para executar o agente.",
            }
        )

    return results


settings = AppConfig()

__all__ = ["AppConfig", "ConfigurationError", "settings", "preflight_config_check"]
