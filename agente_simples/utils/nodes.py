"""Core nodes used by the simple LangGraph agent."""
from __future__ import annotations

import time
from typing import Dict, List, Union

from langchain_core.messages import BaseMessage

from agente_simples.config import ConfigurationError, config
from agente_simples.state import (
    DEFAULT_STATUS_COMPLETED,
    DEFAULT_STATUS_ERROR,
    DEFAULT_STATUS_RESPONDED,
    DEFAULT_STATUS_VALIDATED,
    DialogueInput,
    GraphState,
)
from agente_simples.utils.logging import get_logger
from agente_simples.utils.prompts import SYSTEM_PROMPT

logger = get_logger(__name__)
MessageInput = Union[Dict[str, str], BaseMessage]


def _extract_user_question(state: GraphState) -> str:
    """Return the most recent user-authored message content, if present."""
    messages: List[MessageInput] = state.get("messages", []) or []
    for message in reversed(messages):
        if isinstance(message, dict):
            if message.get("role") == "user":
                return message.get("content", "").strip()
        elif isinstance(message, BaseMessage):
            if getattr(message, "type", None) in {"human", "user"}:
                return getattr(message, "content", "").strip()
    return ""


def validate_question_node(state: GraphState) -> Dict[str, object]:
    """Validate user input and prepare metadata for downstream nodes."""

    question = _extract_user_question(state)
    dialogue = DialogueInput(pergunta=question)
    logger.debug("Pergunta validada", extra={"question": dialogue.pergunta})

    return {
        "metadata": {
            "question": dialogue.pergunta,
            "system_prompt": SYSTEM_PROMPT,
            "started_at": time.time(),
        },
        "status": DEFAULT_STATUS_VALIDATED,
        "messages": [dialogue.as_message()],
    }


def invoke_model_node(state: GraphState) -> Dict[str, object]:
    """Call the configured LLM and capture the response or a friendly error."""

    question: str = state.get("metadata", {}).get("question", "")
    if not question:
        logger.error("Pergunta ausente ao chamar o modelo")
        return {
            "status": DEFAULT_STATUS_ERROR,
            "resposta": (
                "Não consegui identificar a pergunta. Forneça detalhes e tente novamente."
            ),
        }

    prompt = f"{SYSTEM_PROMPT}\n\nPergunta: {question}".strip()

    try:
        llm = config.create_llm()
        generation = llm.invoke(prompt)
        answer = getattr(generation, "content", str(generation))
        status = DEFAULT_STATUS_RESPONDED
        logger.info("Resposta obtida do modelo", extra={"question": question})
    except ConfigurationError as exc:
        logger.error("Configuração inválida ao chamar modelo", extra={"error": str(exc)})
        answer = str(exc)
        status = DEFAULT_STATUS_ERROR
    except Exception:  # pragma: no cover - fallback path exercitado em testes de US2
        logger.exception("Falha ao chamar o modelo", extra={"question": question})
        answer = (
            "Enfrentei um problema ao acessar o modelo agora. "
            "Revise sua conexão ou tente novamente em instantes."
        )
        status = DEFAULT_STATUS_ERROR

    return {
        "resposta": answer,
        "status": status,
    }


def format_answer_node(state: GraphState) -> Dict[str, object]:
    """Format the final answer and record duration metadata."""

    response = state.get("resposta", "")
    started_at = state.get("metadata", {}).get("started_at")
    duration = None
    if started_at is not None:
        duration = max(time.time() - started_at, 0.0)

    formatted = f"Resposta do agente: {response.strip()}"
    is_error = state.get("status") == DEFAULT_STATUS_ERROR

    if is_error:
        logger.warning("Resposta final contém erro controlado")
        update_status = DEFAULT_STATUS_ERROR
    else:
        logger.info("Resposta formatada entregue ao usuário")
        update_status = DEFAULT_STATUS_COMPLETED

    update: Dict[str, object] = {
        "resposta": formatted,
        "status": update_status,
    }

    if duration is not None:
        update["duration_seconds"] = duration

    return update


__all__ = [
    "validate_question_node",
    "invoke_model_node",
    "format_answer_node",
]
