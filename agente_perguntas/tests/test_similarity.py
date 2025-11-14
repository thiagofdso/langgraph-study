from __future__ import annotations

from agente_perguntas.utils.prompts import FAQ_ENTRIES
from agente_perguntas.utils.similarity import (
    meets_threshold,
    rank_faq_by_similarity,
    score_similarity,
)


def test_score_similarity_handles_case_and_whitespace() -> None:
    question = "  Como ALTERO   minha senha?"
    candidate = "Como altero minha senha?"
    assert score_similarity(question, candidate) == 1.0


def test_rank_faq_by_similarity_returns_best_entry_first() -> None:
    question = "Quais formas de pagamento vocês aceitam?"
    ranked = rank_faq_by_similarity(question, FAQ_ENTRIES)
    assert ranked[0].entry["question"] == question
    assert ranked[0].score == 1.0


def test_meets_threshold_respects_tolerance() -> None:
    assert meets_threshold(0.69, 0.7, tolerance=0.02)
    assert not meets_threshold(0.5, 0.7)
