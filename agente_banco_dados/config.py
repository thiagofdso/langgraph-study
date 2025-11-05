"""Configuration helpers and constants for the SQLite sales agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sales.db"

MIN_SEED_PRODUCTS = 5
MIN_SEED_SELLERS = 3
MIN_SEED_SALES = 20

TOP_N_PRODUCTS = 3
TOP_N_SELLERS = 3

DEFAULT_MODEL_ID = "gemini-2.5-flash"


class ConfigurationError(RuntimeError):
    """Raised when mandatory configuration values are missing."""


@dataclass
class AppConfig:
    """Centralised runtime configuration for the sales report agent."""

    model_name: str = os.getenv("GEMINI_MODEL", DEFAULT_MODEL_ID)
    temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.25"))
    timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "30"))
    locale: str = os.getenv("AGENT_LOCALE", "pt-BR")
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")

    def create_llm(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini chat model with the configured credentials."""

        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY ausente. Configure agente_banco_dados/.env antes de gerar insights."
            )
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )


config = AppConfig()
