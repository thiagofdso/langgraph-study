"""Node implementations for the agente_mcp LangGraph workflow."""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, Iterable, Mapping

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from structlog.stdlib import BoundLogger

from agente_mcp.config import AppConfig
from agente_mcp.state import AgentSession, ErrorEntry, RunLogEntry
from agente_mcp.utils.logging import log_tool_event

STATUS_ERROR = "error"
STATUS_VALIDATED = "validated"
STATUS_COMPLETED = "completed"


def _find_last_human_message(messages: Iterable[BaseMessage]) -> HumanMessage | None:
    for message in reversed(list(messages)):
        if isinstance(message, HumanMessage):
            return message
    return None


def validate_input(
    state: AgentSession,
    *,
    app_config: AppConfig,
    logger: BoundLogger,
) -> Dict[str, Any]:
    """Ensure the session contains a valid user question before invoking the LLM."""

    messages = state.get("messages") or []
    human_message = _find_last_human_message(messages)
    if human_message is None:
        logger.error("Nenhuma mensagem do usuário encontrada para validação")
        error: ErrorEntry = {
            "category": "validation",
            "message": "Envie ao menos uma pergunta antes de executar o agente.",
            "details": {"thread_id": state.get("thread_id", app_config.thread_id)},
        }
        return {"status": STATUS_ERROR, "errors": [error]}

    question = human_message.content.strip()
    if not question:
        logger.error("Pergunta vazia recebida", thread_id=state.get("thread_id"))
        error = {
            "category": "validation",
            "message": "A pergunta não pode estar vazia.",
            "details": {"thread_id": state.get("thread_id", app_config.thread_id)},
        }
        return {"status": STATUS_ERROR, "errors": [error]}

    metadata_update = {
        "question": question,
        "thread_id": state.get("thread_id", app_config.thread_id),
    }
    logger.info("Pergunta validada", question=question)
    return {"status": STATUS_VALIDATED, "metadata": metadata_update}


async def invoke_llm(
    state: AgentSession,
    *,
    llm_with_tools: Any,
    logger: BoundLogger,
) -> Dict[str, Any]:
    """Call the bound LLM with the accumulated message history."""

    messages = state.get("messages") or []
    logger.info("Invocando LLM", message_count=len(messages))
    response = await asyncio.to_thread(llm_with_tools.invoke, messages)
    return {"messages": [response]}


async def execute_tools(
    state: AgentSession,
    *,
    tools: Mapping[str, BaseTool],
    logger: BoundLogger,
) -> Dict[str, Any]:
    """Execute the tools requested by the last AI message."""

    messages = state.get("messages") or []
    if not messages:
        logger.error("Estado sem mensagens ao executar ferramentas")
        error: ErrorEntry = {
            "category": "tool_call",
            "message": "Não foi possível executar ferramentas: estado vazio.",
            "details": {},
        }
        return {"status": STATUS_ERROR, "errors": [error]}

    ai_message = messages[-1]
    tool_calls = getattr(ai_message, "tool_calls", None) or []
    if not tool_calls:
        logger.info("Nenhum tool_call encontrado; avanço direto")
        return {}

    tool_messages: list[ToolMessage] = []
    run_entries: list[RunLogEntry] = []
    errors: list[ErrorEntry] = []

    for call in tool_calls:
        tool_name = call.get("name") or "unknown"
        tool_args = call.get("args", {})
        started = time.perf_counter()
        status = "success"
        content: str

        tool = tools.get(tool_name)
        if tool is None:
            status = "error"
            content = f"Ferramenta '{tool_name}' não está disponível."
            errors.append(
                {
                    "category": "tool_call",
                    "message": content,
                    "details": {"tool_name": tool_name},
                }
            )
        else:
            try:
                result = await tool.ainvoke(tool_args)
                if isinstance(result, str):
                    content = result
                else:
                    content = json.dumps(result, ensure_ascii=False)
            except Exception as exc:  # pragma: no cover - defensive logging
                status = "error"
                content = f"Erro ao executar {tool_name}: {exc}"
                errors.append(
                    {
                        "category": "tool_execution",
                        "message": content,
                        "details": {"tool_name": tool_name},
                    }
                )
        duration_ms = int((time.perf_counter() - started) * 1000)
        log_tool_event(
            logger,
            tool_name=tool_name,
            status=status,
            duration_ms=duration_ms,
            args=tool_args,
        )
        run_entries.append(
            {
                "phase": "execute_tools",
                "tool_name": tool_name,
                "status": status,
                "duration_ms": duration_ms,
                "message": content if status == "error" else "ok",
            }
        )
        tool_messages.append(
            ToolMessage(
                content=content,
                name=tool_name,
                tool_call_id=call.get("id", "unknown"),
            )
        )

    payload: Dict[str, Any] = {
        "messages": tool_messages,
        "run_log": run_entries,
    }
    if errors:
        payload["errors"] = errors
        payload["status"] = STATUS_ERROR
    return payload


def format_response(state: AgentSession, *, logger: BoundLogger) -> Dict[str, Any]:
    """Finalize the interaction and record completion metadata."""

    messages = state.get("messages") or []
    final_message = "Não foi possível gerar uma resposta."
    ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
    if ai_messages:
        final_message = ai_messages[-1].content
    logger.info("Sessão concluída", response=final_message)
    run_entry: RunLogEntry = {
        "phase": "format_response",
        "tool_name": "n/a",
        "status": "completed",
        "duration_ms": 0,
        "message": "Resposta final formatada",
    }
    return {
        "status": STATUS_COMPLETED,
        "run_log": [run_entry],
        "metadata": {"completed_at": time.time()},
    }


def handle_error(state: AgentSession, *, logger: BoundLogger) -> Dict[str, Any]:
    """Transform accumulated errors into a final assistant message."""

    errors = state.get("errors") or []
    if errors:
        message = errors[-1].get("message", "Ocorreu um erro durante a execução.")
    else:
        message = "Ocorreu um erro durante a execução."
    logger.error("Fluxo encerrado com erro", message=message)
    ai_message = AIMessage(content=message)
    return {"messages": [ai_message], "status": STATUS_ERROR}


__all__ = [
    "execute_tools",
    "format_response",
    "handle_error",
    "invoke_llm",
    "validate_input",
]
