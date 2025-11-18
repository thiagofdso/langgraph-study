"""Structured logging utilities for agente_mcp."""
from __future__ import annotations

import logging
import os
from logging import Handler
from pathlib import Path
from typing import Any

import structlog

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOGGER_NAME = "agente_mcp"
_FILE_HANDLER_ID = f"{_LOGGER_NAME}.file"
_CONSOLE_HANDLER_ID = f"{_LOGGER_NAME}.console"


def _resolve_log_dir(value: str | Path | None = None) -> Path:
    if value is None:
        env_value = os.environ.get("AGENTE_MCP_LOG_DIR")
        if env_value is not None:
            value = env_value
        else:
            value = DEFAULT_LOG_DIR
    return Path(value).expanduser()


LOG_DIR = _resolve_log_dir()
LOG_DIR.mkdir(parents=True, exist_ok=True)


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


def _ensure_console_handler(root: logging.Logger) -> None:
    if any(handler.get_name() == _CONSOLE_HANDLER_ID for handler in root.handlers):
        return
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    console.setFormatter(formatter)
    console.set_name(_CONSOLE_HANDLER_ID)
    root.addHandler(console)


def _configure_standard_logging(*, enable_file_handler: bool) -> None:
    root = logging.getLogger(_LOGGER_NAME)
    root.setLevel(logging.INFO)

    if enable_file_handler:
        if not any(handler.get_name() == _FILE_HANDLER_ID for handler in root.handlers):
            root.addHandler(_build_file_handler())
    else:
        _remove_file_handler(root)

    _ensure_console_handler(root)

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
    """Override the directory used for log persistence."""

    global LOG_DIR
    new_dir = _resolve_log_dir(path)
    if new_dir == LOG_DIR:
        return LOG_DIR
    LOG_DIR = new_dir
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    _remove_file_handler(logging.getLogger(_LOGGER_NAME))
    return LOG_DIR


def setup_logging(*, enable_file_handler: bool = True) -> structlog.stdlib.BoundLogger:
    """Configure structlog and stdlib logging, returning a bound logger."""

    _configure_standard_logging(enable_file_handler=enable_file_handler)
    return structlog.get_logger(_LOGGER_NAME).bind(log_dir=str(LOG_DIR))


def log_tool_event(logger: structlog.stdlib.BoundLogger, **payload: Any) -> None:
    """Emit a structured log entry dedicated to tool-call tracking."""

    logger.info("tool_event", **payload)


__all__ = [
    "DEFAULT_LOG_DIR",
    "LOG_DIR",
    "log_tool_event",
    "set_log_dir",
    "setup_logging",
]
