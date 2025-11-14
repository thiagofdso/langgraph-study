"""Graph node implementations for agente_perguntas."""

from __future__ import annotations

from typing import Any, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.types import Command, interrupt
from structlog.stdlib import BoundLogger
from typing_extensions import TypedDict

from agente_perguntas.config import AppConfig
from agente_perguntas.state import AgentState
from agente_perguntas.utils.prompts import FAQEntry, get_faq_entries
from agente_perguntas.utils.similarity import RankedFAQ, meets_threshold, rank_faq_by_similarity

ESCALATION_MESSAGE = (
    "Não encontrei a resposta no FAQ. Encaminharei sua dúvida para um especialista humano."
)
DEFAULT_NOTES = "Encaminhamento registrado manualmente."
EMPTY_QUESTION_MESSAGE = "Não recebemos uma pergunta válida. Informe uma dúvida para continuar."


MessageLike = BaseMessage | dict[str, Any]


class HumanEscalationPayload(TypedDict):
    """Payload delivered to HITL operators via LangGraph interrupts."""

    question: str
    best_match: str
    best_match_confidence: float
    faq_reference: list[FAQEntry]


def _build_payload(
    question: str, best: RankedFAQ, faq_reference: list[FAQEntry]
) -> HumanEscalationPayload:
    return HumanEscalationPayload(
        question=question,
        best_match=best.entry["question"],
        best_match_confidence=round(best.score, 4),
        faq_reference=faq_reference,
    )


def _normalize_content(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts: list[str] = []
        for chunk in value:
            if isinstance(chunk, dict):
                text = chunk.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return " ".join(parts).strip()
    return str(value).strip()


def _latest_question(messages: Sequence[MessageLike]) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return _normalize_content(message.content)
        if isinstance(message, BaseMessage):
            if getattr(message, "type", "") == "human":
                return _normalize_content(message.content)
        if isinstance(message, dict):
            role = str(message.get("role", "")).lower()
            if role in {"user", "human"}:
                return _normalize_content(message.get("content", ""))
    return ""


def _assistant_response(content: str) -> list[AIMessage]:
    return [AIMessage(content=content)]


def evaluate_question(
    state: AgentState,
    *,
    settings: AppConfig,
    logger: BoundLogger,
    faq_entries: list[FAQEntry] | None = None,
) -> AgentState:
    """Evaluate a question and either answer automatically or trigger HITL."""

    messages: Sequence[MessageLike] = state.get("messages", [])
    question = _latest_question(messages)
    if not question:
        logger.warning("question_missing", status="encaminhar para humano")
        return {
            "answer": EMPTY_QUESTION_MESSAGE,
            "confidence": 0.0,
            "status": "encaminhar para humano",
            "notes": "Pergunta vazia informada pelo operador.",
            "messages": _assistant_response(EMPTY_QUESTION_MESSAGE),
        }

    entries = faq_entries or get_faq_entries()
    ranked = rank_faq_by_similarity(question, entries)
    if not ranked:
        raise ValueError("Nenhuma entrada de FAQ disponível para avaliação.")
    best = ranked[0]

    if meets_threshold(best.score, settings.confidence_threshold):
        logger.info(
            "auto_answer",
            question=question,
            answer=best.entry["answer"],
            confidence=best.score,
        )
        answer_text = best.entry["answer"]
        return {
            "answer": answer_text,
            "confidence": best.score,
            "status": "respondido automaticamente",
            "notes": f"Correspondência: {best.entry['question']}",
            "messages": _assistant_response(answer_text),
        }

    payload = _build_payload(question, best, entries)
    logger.info(
        "escalate_required",
        question=question,
        best_match=payload["best_match"],
        confidence=best.score,
    )
    human_payload = interrupt(payload)
    human_message = human_payload.get("message") or ESCALATION_MESSAGE
    human_notes = human_payload.get("notes") or DEFAULT_NOTES
    return {
        "answer": human_message,
        "confidence": best.score,
        "status": "encaminhar para humano",
        "notes": human_notes,
        "messages": _assistant_response(human_message),
    }


def resume_with_human_response(
    graph: Any,
    *,
    config: dict[str, Any],
    message: str,
    notes: str,
) -> AgentState:
    """Resume the LangGraph execution with manual input from a specialist."""

    response = {"message": message, "notes": notes}
    for _ in graph.stream(Command(resume=response), config=config):
        pass
    state = graph.get_state(config)
    return state.values  # type: ignore[return-value]


__all__ = ["evaluate_question", "resume_with_human_response", "ESCALATION_MESSAGE", "DEFAULT_NOTES"]
