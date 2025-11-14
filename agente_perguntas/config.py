"""Configuration helpers for the agente_perguntas package."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from agente_perguntas.utils.logging import LOG_DIR

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_CONFIDENCE = 0.7


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    """Clamp *value* into the inclusive range ``[minimum, maximum]``."""
    return max(minimum, min(maximum, value))


def _parse_float(raw: str | None, fallback: float) -> float:
    """Return ``raw`` converted to ``float`` or ``fallback`` when invalid."""
    try:
        return float(raw) if raw is not None else fallback
    except (TypeError, ValueError):
        return fallback


@dataclass(frozen=True)
class AppConfig:
    """Centralized runtime configuration loaded from environment variables."""

    gemini_api_key: str
    model_name: str
    temperature: float
    confidence_threshold: float
    log_dir: Path

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment variables with validation."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY não configurado. Copie .env.example e defina a chave antes de executar o agente."
            )

        model_name = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
        temperature = _clamp(_parse_float(os.environ.get("GEMINI_TEMPERATURE"), DEFAULT_TEMPERATURE))
        confidence = _clamp(
            _parse_float(os.environ.get("AGENTE_PERGUNTAS_CONFIDENCE"), DEFAULT_CONFIDENCE)
        )
        return cls(
            gemini_api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            confidence_threshold=confidence,
            log_dir=LOG_DIR,
        )


__all__ = ["AppConfig", "DEFAULT_MODEL", "DEFAULT_TEMPERATURE", "DEFAULT_CONFIDENCE"]
