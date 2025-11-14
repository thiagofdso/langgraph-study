"""Similarity helpers used to score FAQ matches."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Sequence

from agente_perguntas.utils.prompts import FAQEntry

_TOKEN_PATTERN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


def _tokenize(text: str) -> set[str]:
    """Return a normalized token set for similarity checks."""
    return {token.lower() for token in _TOKEN_PATTERN.findall(text)}


def score_similarity(user_question: str, candidate_question: str) -> float:
    """Compute the overlap ratio between the user question and a FAQ question."""
    user_tokens = _tokenize(user_question)
    candidate_tokens = _tokenize(candidate_question)
    if not user_tokens or not candidate_tokens:
        return 0.0
    intersection = user_tokens & candidate_tokens
    denominator = max(len(user_tokens), len(candidate_tokens))
    return len(intersection) / denominator if denominator else 0.0


@dataclass(slots=True)
class RankedFAQ:
    """Represents a FAQ entry paired with its similarity score."""

    entry: FAQEntry
    score: float


def rank_faq_by_similarity(question: str, entries: Sequence[FAQEntry]) -> list[RankedFAQ]:
    """Return entries (highest score first) for the supplied ``question``."""
    normalized_question = question.strip()
    ranked: List[RankedFAQ] = []
    for entry in entries:
        score = score_similarity(normalized_question, entry["question"])
        ranked.append(RankedFAQ(entry=entry, score=score))
    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked


def meets_threshold(score: float, threshold: float, *, tolerance: float = 1e-6) -> bool:
    """Return ``True`` if ``score`` satisfies ``threshold`` considering tolerance."""
    return score + tolerance >= threshold


def top_match(question: str, entries: Sequence[FAQEntry]) -> RankedFAQ:
    """Convenience helper returning only the best match for ``question``."""
    if not entries:
        raise ValueError("A lista de FAQ não pode estar vazia ao calcular similaridade.")
    ranked = rank_faq_by_similarity(question, entries)
    return ranked[0] if ranked else RankedFAQ(entry=entries[0], score=0.0)


__all__ = ["RankedFAQ", "rank_faq_by_similarity", "score_similarity", "meets_threshold", "top_match"]
