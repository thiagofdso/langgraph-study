"""Centralized configuration helpers for the agente_web project."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver

_ENV_PATH = Path(__file__).resolve().parent / ".env"
if _ENV_PATH.exists():
    load_dotenv(dotenv_path=_ENV_PATH)
else:
    load_dotenv()


class ConfigurationError(RuntimeError):
    """Raised when required configuration values are missing or invalid."""


@dataclass
class AppConfig:
    """Runtime configuration for the agente_web agent."""

    default_question: str = os.getenv("DEFAULT_QUESTION", "Como pesquisar arquivos no linux?")
    tavily_api_key: Optional[str] = os.getenv("TAVILY_API_KEY")
    tavily_max_results: int = int(os.getenv("TAVILY_MAX_RESULTS", "5"))
    tavily_topic: str = os.getenv("TAVILY_TOPIC", "general")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    default_thread_id: str = os.getenv("DEFAULT_THREAD_ID", "agente-web-cli")
    summary_max_sources: int = int(os.getenv("SUMMARY_MAX_SOURCES", "5"))

    def _ensure_tavily_credentials(self) -> None:
        if not self.tavily_api_key:
            raise ConfigurationError(
                "TAVILY_API_KEY ausente. Configure o arquivo .env (copie .env.example) antes de executar o agente."
            )

    def _ensure_gemini_credentials(self) -> None:
        if not self.gemini_api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY ausente. Configure o arquivo .env (copie .env.example) antes de executar o agente."
            )

    def create_search_tool(self) -> TavilySearch:
        """Instantiate the Tavily search tool respecting project defaults."""

        self._ensure_tavily_credentials()
        os.environ.setdefault("TAVILY_API_KEY", self.tavily_api_key or "")
        return TavilySearch(
            max_results=self.tavily_max_results,
            topic=self.tavily_topic,
            tavily_api_key=self.tavily_api_key,
        )

    def create_model(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini chat model for summarization."""

        self._ensure_gemini_credentials()
        os.environ.setdefault("GOOGLE_API_KEY", self.gemini_api_key or "")
        return ChatGoogleGenerativeAI(
            model=self.gemini_model,
            temperature=self.gemini_temperature,
            api_key=self.gemini_api_key,
        )

    def create_checkpointer(self) -> MemorySaver:
        """Return an in-memory checkpointer suitable for local runs."""

        return MemorySaver()


config = AppConfig()

