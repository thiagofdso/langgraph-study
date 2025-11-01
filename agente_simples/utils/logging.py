"""Logging utilities for the simple agent."""
from __future__ import annotations

import logging
import os
from pathlib import Path

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR = Path(os.getenv("AGENTE_SIMPLES_LOG_DIR", DEFAULT_LOG_DIR))
LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def _configure_stream_handler(formatter: logging.Formatter) -> logging.Handler:
    """Create a stream handler configured with the shared formatter."""
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    return handler


def _configure_file_handler(formatter: logging.Formatter) -> logging.Handler:
    """Create a file handler that writes to the configured log directory."""
    handler = logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8")
    handler.setFormatter(formatter)
    return handler


def get_logger(name: str = "agente_simples", level: int = logging.INFO) -> logging.Logger:
    """Return a logger configured with stream and file handlers."""

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(_LOG_FORMAT)
    desired_path = LOG_DIR / "agent.log"

    needs_stream = True
    needs_file = True

    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            handler_path = Path(getattr(handler, "baseFilename", ""))
            if handler_path != desired_path:
                logger.removeHandler(handler)
                handler.close()
            else:
                needs_file = False
        elif isinstance(handler, logging.StreamHandler):
            needs_stream = False

    if needs_stream:
        logger.addHandler(_configure_stream_handler(formatter))

    if needs_file:
        logger.addHandler(_configure_file_handler(formatter))

    return logger


__all__ = ["get_logger", "LOG_DIR", "DEFAULT_LOG_DIR"]
