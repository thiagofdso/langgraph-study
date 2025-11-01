
"""Core nodes for the memory agent graph."""
from __future__ import annotations

import time
from typing import Dict

from agente_memoria.config import config
from agente_memoria.state import GraphState
from agente_memoria.utils.logging import get_logger

logger = get_logger(__name__)


def validate_question_node(state: GraphState) -> Dict[str, object]:
    """Validate user input and prepare metadata."""
    logger.info("Validando pergunta do usuário...")
    question = state.get("messages", [])[-1].content
    if len(question) < 5:
        return {
            "status": "error",
            "error": "A pergunta é muito curta. Por favor, forneça mais detalhes.",
        }
    return {
        "metadata": {
            "question": question,
            "started_at": time.time(),
        },
        "status": "validated",
    }


def load_history_node(state: GraphState) -> Dict[str, object]:
    """Load conversation history from the checkpointer."""
    logger.info(f"Carregando histórico para thread_id: {state['thread_id']}")
    # This is a placeholder. The actual history is loaded by the checkpointer.
    return {}


def invoke_model_node(state: GraphState) -> Dict[str, object]:
    """Invoke the LLM with the conversation history."""
    logger.info("Invocando o modelo...")
    llm = config.create_llm()
    try:
        response = llm.invoke(state["messages"])
        logger.info("Invocação do modelo bem-sucedida.")
        return {
            "messages": [response],
            "status": "responded",
        }
    except Exception as e:
        logger.error(f"Falha na invocação do modelo: {e}")
        return {
            "status": "error",
            "error": "Falha ao obter uma resposta do modelo.",
        }


def update_memory_node(state: GraphState) -> Dict[str, object]:
    """Update the conversation history."""
    logger.info("Atualizando memória...")
    # The checkpointer automatically saves the state, including messages.
    return {}


def format_response_node(state: GraphState) -> Dict[str, object]:
    """Format the final response and calculate duration."""
    logger.info("Formatando a resposta...")
    response = state.get("messages", [])[-1].content
    started_at = state.get("metadata", {}).get("started_at")
    duration = time.time() - started_at if started_at is not None else 0

    return {
        "resposta": f"Resposta do agente: {response}",
        "duration_seconds": duration,
        "status": "completed",
    }
