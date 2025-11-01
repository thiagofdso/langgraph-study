"""Configuration helpers for the simple LangGraph agent."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing or invalid."""


@dataclass
class AppConfig:
    """Centralized configuration for the simple agent."""

    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
    timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
    locale: str = os.getenv("AGENT_LOCALE", "pt-BR")
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    def create_llm(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini chat model using current settings."""

        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY ausente. Configure .env ou variável de ambiente antes de executar o agente."
            )
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )

    def checkpointer_enabled(self) -> bool:
        """Return False because this agent runs without checkpointing."""

        return False


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
                "message": "Valor fora do intervalo [0,1]; considere ajustar para manter respostas estáveis.",
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
