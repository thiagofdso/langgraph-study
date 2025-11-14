"""Convenient exports for agente_perguntas utility modules."""

from __future__ import annotations

from .prompts import (
    DEMO_QUESTIONS,
    FAQEntry,
    FAQ_ENTRIES,
    build_system_prompt,
    get_faq_entries,
    list_faq_questions,
)
from .similarity import RankedFAQ, meets_threshold, rank_faq_by_similarity, score_similarity, top_match
from .logging import log_interaction, setup_logging

__all__ = [
    "DEMO_QUESTIONS",
    "FAQEntry",
    "FAQ_ENTRIES",
    "build_system_prompt",
    "get_faq_entries",
    "list_faq_questions",
    "rank_faq_by_similarity",
    "score_similarity",
    "top_match",
    "meets_threshold",
    "log_interaction",
    "setup_logging",
    "RankedFAQ",
]
