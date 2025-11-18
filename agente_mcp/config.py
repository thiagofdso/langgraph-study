"""Application configuration helpers for agente_mcp."""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver

DEFAULT_ENV_PATH = Path(__file__).resolve().parent / ".env"
DEFAULT_ROOT_ENV = Path(".env")
_DEFAULT_QUESTIONS = [
    "quanto é 150 vezes 3?",
    "qual o clima em Nova York?",
]


class ConfigError(RuntimeError):
    """Raised when the agente_mcp configuration is invalid."""


@dataclass(slots=True)
class AppConfig:
    """Dataclass containing the validated runtime configuration."""

    gemini_api_key: str
    google_api_key: str | None = None
    default_questions: list[str] = field(default_factory=list)
    auto_start_servers: bool = True
    log_level: str = "INFO"
    thread_id: str = "manual-run"
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.0

    def as_dict(self) -> dict[str, str | list[str] | bool]:
        """Return a shallow dictionary representation useful for logging."""

        return {
            "gemini_api_key": "***" if self.gemini_api_key else "",
            "google_api_key": "***" if self.google_api_key else "",
            "default_questions": list(self.default_questions),
            "auto_start_servers": self.auto_start_servers,
            "log_level": self.log_level,
            "thread_id": self.thread_id,
            "model_name": self.model_name,
            "temperature": self.temperature,
        }

    def create_llm(self) -> ChatGoogleGenerativeAI:
        """Instantiate the Gemini model configured for the agent."""

        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.gemini_api_key,
        )

    def create_checkpointer(self):
        """Return the configured LangGraph checkpointer."""

        return MemorySaver()


def _load_env_files(dotenv_path: str | os.PathLike[str] | None = None) -> None:
    """Load environment variables from the provided path plus defaults."""

    candidates: list[Path] = []
    if dotenv_path is not None:
        candidates.append(Path(dotenv_path))
    candidates.append(DEFAULT_ENV_PATH)
    candidates.append(DEFAULT_ROOT_ENV)

    seen: set[Path] = set()
    for path in candidates:
        resolved = path.expanduser().resolve()
        if resolved in seen or not resolved.exists():
            continue
        load_dotenv(resolved, override=False)
        seen.add(resolved)


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_questions(raw_value: str | None, fallback: Sequence[str]) -> list[str]:
    questions: list[str] = []
    if raw_value:
        try:
            loaded = json.loads(raw_value)
            if isinstance(loaded, Sequence) and not isinstance(loaded, (str, bytes)):
                questions = [str(item).strip() for item in loaded if str(item).strip()]
        except json.JSONDecodeError:
            questions = [segment.strip() for segment in raw_value.split("\n") if segment.strip()]
    if not questions:
        questions = [item for item in fallback if item.strip()]
    if not questions:
        msg = "Defina pelo menos uma pergunta padrão para demonstração."
        raise ConfigError(msg)
    return questions


def load_app_config(
    *,
    dotenv_path: str | os.PathLike[str] | None = None,
    overrides: dict[str, str] | None = None,
    use_dotenv: bool = True,
) -> AppConfig:
    """Load and validate AppConfig from environment variables."""

    if use_dotenv:
        _load_env_files(dotenv_path)
    env = dict(os.environ)
    if overrides:
        env.update(overrides)

    gemini_api_key = env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY")
    if not gemini_api_key:
        raise ConfigError("Defina GEMINI_API_KEY no arquivo .env ou nas variáveis de ambiente.")

    default_questions = _parse_questions(env.get("MCP_DEFAULT_QUESTIONS"), _DEFAULT_QUESTIONS)
    auto_start = _parse_bool(env.get("MCP_AUTO_START_SERVERS"), True)
    log_level = (env.get("MCP_LOG_LEVEL") or "INFO").upper()
    thread_id = (env.get("MCP_THREAD_ID") or "manual-run").strip() or "manual-run"
    model_name = env.get("MCP_MODEL_NAME") or "gemini-2.5-flash"
    try:
        temperature = float(env.get("MCP_TEMPERATURE", "0.0"))
    except ValueError as exc:  # pragma: no cover - defensive parsing
        raise ConfigError("MCP_TEMPERATURE deve ser numérico.") from exc

    return AppConfig(
        gemini_api_key=gemini_api_key,
        google_api_key=env.get("GOOGLE_API_KEY"),
        default_questions=default_questions,
        auto_start_servers=auto_start,
        log_level=log_level,
        thread_id=thread_id,
        model_name=model_name,
        temperature=temperature,
    )


__all__ = ["AppConfig", "ConfigError", "load_app_config"]
