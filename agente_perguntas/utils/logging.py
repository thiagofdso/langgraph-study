"""Structured logging helpers for agente_perguntas."""

from __future__ import annotations

import logging
import os
from logging import Handler
from pathlib import Path
from typing import Any, NamedTuple

import structlog

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


def _resolve_log_dir(value: str | Path | None = None) -> Path:
    """Return the logging directory determined by explicit value or environment."""
    if value is None:
        env_value = os.environ.get("AGENTE_PERGUNTAS_LOG_DIR")
        if env_value is not None:
            value = env_value
        else:
            value = DEFAULT_LOG_DIR
    return Path(value).expanduser()


LOG_DIR = _resolve_log_dir()
LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOGGER_NAME = "agente_perguntas"
_FILE_HANDLER_ID = f"{_LOGGER_NAME}.file"
_CONSOLE_HANDLER_ID = f"{_LOGGER_NAME}.console"


class _ConfigKey(NamedTuple):
    log_dir: Path | None
    file_logging: bool


_CONFIGURED_FOR: _ConfigKey | None = None


def _build_file_handler() -> Handler:
    handler = logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s :: %(message)s", "%%Y-%%m-%%d %%H:%%M:%%S"
    )
    handler.setFormatter(formatter)
    handler.set_name(_FILE_HANDLER_ID)
    return handler


def _remove_file_handler(root: logging.Logger) -> None:
    for handler in list(root.handlers):
        if handler.get_name() == _FILE_HANDLER_ID:
            root.removeHandler(handler)
            handler.close()


def _configure_standard_logging(*, enable_file_handler: bool) -> None:
    root = logging.getLogger(_LOGGER_NAME)
    root.setLevel(logging.INFO)

    if enable_file_handler:
        if not any(existing.get_name() == _FILE_HANDLER_ID for existing in root.handlers):
            root.addHandler(_build_file_handler())
    else:
        _remove_file_handler(root)

    if not any(existing.get_name() == _CONSOLE_HANDLER_ID for existing in root.handlers):
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter("%(message)s")
        console.setFormatter(formatter)
        console.set_name(_CONSOLE_HANDLER_ID)
        root.addHandler(console)

    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def set_log_dir(path: str | Path | None = None) -> Path:
    """Override the active log directory (used mainly for tests)."""
    global LOG_DIR, _CONFIGURED_FOR
    new_dir = _resolve_log_dir(path)
    if new_dir != LOG_DIR:
        LOG_DIR = new_dir
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        _remove_file_handler(logging.getLogger(_LOGGER_NAME))
        _CONFIGURED_FOR = None
    return LOG_DIR


def setup_logging(*, enable_file_handler: bool = True) -> structlog.stdlib.BoundLogger:
    """Configure structlog + stdlib logging and return a bound logger."""

    global _CONFIGURED_FOR
    key = _ConfigKey(LOG_DIR if enable_file_handler else None, enable_file_handler)
    if _CONFIGURED_FOR != key:
        _configure_standard_logging(enable_file_handler=enable_file_handler)
        _CONFIGURED_FOR = key
    return structlog.get_logger(_LOGGER_NAME).bind(log_dir=str(LOG_DIR))


def log_interaction(logger: structlog.stdlib.BoundLogger, **payload: Any) -> None:
    """Log a structured interaction payload using a shared schema."""
    logger.info("interaction", **payload)


__all__ = [
    "DEFAULT_LOG_DIR",
    "LOG_DIR",
    "log_interaction",
    "set_log_dir",
    "setup_logging",
]
