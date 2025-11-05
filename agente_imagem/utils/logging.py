"""Logging utilities for the imagem agent refactor."""

from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: str, *, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger sharing the project formatting conventions."""

    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
