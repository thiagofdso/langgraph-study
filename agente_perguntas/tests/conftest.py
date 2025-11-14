from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict

import pytest

from langgraph.checkpoint.memory import InMemorySaver

from agente_perguntas.config import AppConfig
from agente_perguntas.graph import build_graph
from agente_perguntas.utils.logging import set_log_dir, setup_logging


@pytest.fixture()
def env_settings(tmp_path, monkeypatch) -> Path:
    """Configure environment variables for tests and return the log directory."""

    log_dir = tmp_path / "logs"
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("AGENTE_PERGUNTAS_LOG_DIR", str(log_dir))
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    monkeypatch.setenv("GEMINI_TEMPERATURE", "0.2")
    monkeypatch.setenv("AGENTE_PERGUNTAS_CONFIDENCE", "0.7")
    set_log_dir(log_dir)
    return log_dir


@pytest.fixture()
def app_config(env_settings: Path) -> AppConfig:
    return AppConfig.load()


@pytest.fixture()
def logger(app_config: AppConfig):
    return setup_logging()


@pytest.fixture()
def graph(app_config: AppConfig, logger):
    return build_graph(app_config, logger, checkpointer=InMemorySaver())


@pytest.fixture()
def thread_config() -> Callable[[str], Dict[str, Dict[str, str]]]:
    def _factory(identifier: str) -> Dict[str, Dict[str, str]]:
        return {"configurable": {"thread_id": identifier}}

    return _factory
