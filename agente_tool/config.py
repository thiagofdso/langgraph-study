"""Configuration helpers for the calculator tool agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing or invalid."""


@dataclass
class AppConfig:
    """Centralized configuration for the agente_tool project."""

    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
    timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    default_thread_id: str = os.getenv("DEFAULT_THREAD_ID", "calculator-cli")

    def create_llm(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini chat model using the current configuration."""

        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY ausente. Configure .env (copie de .env.example) antes de executar o agente."
            )
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )

    def create_checkpointer(self) -> MemorySaver:
        """Return an in-memory checkpointer for LangGraph runs."""

        return MemorySaver()

    def create_model_with_tools(self, tools: Sequence[Any]):
        """Instantiate the chat model already bound to the provided tools."""

        model = self.create_llm()
        return model.bind_tools(tools)


config = AppConfig()


def preflight_config_check() -> List[Dict[str, str]]:
    """Return diagnostic results for required configuration values."""

    results: List[Dict[str, str]] = []

    if config.api_key:
        results.append(
            {
                "name": "GEMINI_API_KEY",
                "result": "pass",
                "message": "Credencial localizada.",
            }
        )
    else:
        results.append(
            {
                "name": "GEMINI_API_KEY",
                "result": "fail",
                "message": (
                    "Configure GEMINI_API_KEY no arquivo .env (copie .env.example) antes de continuar."
                ),
            }
        )

    if not 0.0 <= config.temperature <= 1.0:
        results.append(
            {
                "name": "GEMINI_TEMPERATURE",
                "result": "warn",
                "message": "Valor fora do intervalo [0,1]; ajuste para manter respostas estáveis.",
            }
        )

    if config.timeout_seconds < 5:
        results.append(
            {
                "name": "AGENT_TIMEOUT_SECONDS",
                "result": "warn",
                "message": "Timeout muito baixo pode interromper respostas; recomenda-se ≥ 5 segundos.",
            }
        )

    return results
