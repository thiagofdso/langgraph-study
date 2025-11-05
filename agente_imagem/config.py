"""Configuration helpers for the imagem agent refactor."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing or invalid."""


@dataclass
class AppConfig:
    """Centralized configuration for the image analysis agent."""

    model_name: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.0"))
    api_key: Optional[str] = os.getenv("GOOGLE_API_KEY") or None
    default_image: str = os.getenv("AGENTE_IMAGEM_DEFAULT_IMAGE", "folder_map.png")

    def require_api_key(self) -> str:
        """Return the configured API key or raise with actionable guidance."""

        if not self.api_key:
            raise ConfigurationError(
                "GOOGLE_API_KEY não configurada. "
                "Defina a variável de ambiente antes de executar o agente."
            )
        return self.api_key

    def create_llm(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini chat model using the current settings."""

        return ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.require_api_key(),
            temperature=self.temperature,
        )


def preflight_config_check() -> List[dict]:
    """Return diagnostic results for required configuration values."""

    results: List[dict] = []

    if config.api_key:
        results.append(
            {"name": "GOOGLE_API_KEY", "result": "pass", "message": "Credencial localizada."}
        )
    else:
        results.append(
            {
                "name": "GOOGLE_API_KEY",
                "result": "fail",
                "message": "Configure GOOGLE_API_KEY no arquivo .env antes de usar o agente.",
            }
        )

    return results


config = AppConfig()
