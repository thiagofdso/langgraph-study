"""Command-line interface for the agente_perguntas LangGraph agent."""

from __future__ import annotations

import argparse
import sys
import uuid
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agente_perguntas.config import AppConfig
from agente_perguntas.graph import build_graph
from agente_perguntas.state import AgentState
from agente_perguntas.utils.logging import log_interaction, setup_logging
from agente_perguntas.utils.nodes import (
    DEFAULT_NOTES,
    ESCALATION_MESSAGE,
    resume_with_human_response,
)
from agente_perguntas.utils.prompts import DEMO_QUESTIONS, build_system_prompt


@dataclass(slots=True)
class InteractionResult:
    """Represents the final state of a single interaction for display/logging."""

    question: str
    answer: str
    confidence: float
    status: str
    notes: str


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="agente_perguntas",
        description="Executa o agente FAQ em modo demo ou pergunta única.",
    )
    parser.add_argument(
        "--pergunta",
        help="Pergunta única a ser respondida. Sem este argumento, o modo demo é executado.",
    )
    parser.add_argument(
        "--thread-id",
        help="Identificador opcional para reutilizar checkpoints do LangGraph.",
    )
    return parser.parse_args(argv)


def _thread_config(thread_id: str | None) -> dict[str, Any]:
    return {"configurable": {"thread_id": thread_id or uuid.uuid4().hex}}


def _build_user_messages(question: str) -> list[HumanMessage]:
    """Return the initial LangChain messages payload for the graph invocation."""

    return [HumanMessage(content=question.strip())]


def _handle_interrupt(payload: dict[str, Any]) -> tuple[str, str]:
    print("-" * 72)
    print("Encaminhar para humano:")
    print(f"Pergunta original: {payload.get('question', '')}")
    best_match = payload.get("best_match")
    if best_match:
        confidence = payload.get("best_match_confidence", 0.0)
        print(f"Melhor correspondência ({confidence:.2f}): {best_match}")
    message = input("Resposta do especialista (enter para padrão): ").strip() or ESCALATION_MESSAGE
    notes = input("Notas do especialista (opcional): ").strip() or DEFAULT_NOTES
    return message, notes


def _finalize_state(state_values: AgentState, question: str) -> InteractionResult:
    return InteractionResult(
        question=question,
        answer=str(state_values.get("answer", "")),
        confidence=float(state_values.get("confidence", 0.0)),
        status=str(state_values.get("status", "desconhecido")),
        notes=str(state_values.get("notes", "")),
    )


def _invoke_graph(graph: Any, question: str, *, thread_id: str | None) -> tuple[AgentState, dict[str, Any] | None, dict[str, Any]]:
    config = _thread_config(thread_id)
    interrupt_payload: dict[str, Any] | None = None
    last_event: dict[str, Any] = {}
    for event in graph.stream({"messages": _build_user_messages(question)}, config=config):
        last_event = event
        interrupt_events = event.get("__interrupt__")
        if interrupt_events:
            interrupt_payload = interrupt_events[0].value  # type: ignore[index]
    return graph.get_state(config).values, interrupt_payload, config


def run_single_question(graph: Any, question: str, *, logger: Any, thread_id: str | None = None) -> InteractionResult:
    state_values, interrupt_payload, config = _invoke_graph(graph, question, thread_id=thread_id)
    final_state = state_values
    if interrupt_payload is not None:
        message, notes = _handle_interrupt(interrupt_payload)
        final_state = resume_with_human_response(
            graph,
            config=config,
            message=message,
            notes=notes,
        )
    result = _finalize_state(final_state, question)
    log_interaction(
        logger,
        question=result.question,
        status=result.status,
        confidence=result.confidence,
        notes=result.notes,
        answer_preview=result.answer,
        mode="single",
    )
    _print_result(result)
    return result


def _print_result(result: InteractionResult) -> None:
    print("Pergunta:", result.question)
    print(f"Status: {result.status} (confiança {result.confidence:.2f})")
    print("Resposta:", result.answer)
    if result.notes:
        print("Notas:", result.notes)
    print()


def run_demo(graph: Any, *, logger: Any) -> None:
    print("=== FAQ Routing Demo ===")
    print()
    interactions: list[InteractionResult] = []
    for index, question in enumerate(DEMO_QUESTIONS, start=1):
        print(f"Processando pergunta demo #{index}...")
        result = run_single_question(graph, question, logger=logger, thread_id=f"demo-{index}")
        interactions.append(result)

    resolved = [item for item in interactions if item.status == "respondido automaticamente"]
    escalated = [item for item in interactions if item.status == "encaminhar para humano"]

    print("Resumo final")
    print("-" * 40)
    if resolved:
        print("Respondidos automaticamente:")
        for item in resolved:
            print(f"• {item.question} (confiança {item.confidence:.2f})")
    else:
        print("Respondidos automaticamente: nenhum")

    print("\nEncaminhados para humano:")
    if escalated:
        for item in escalated:
            print(f"• {item.question} (confiança {item.confidence:.2f})")
    else:
        print("• Nenhuma pergunta pendente")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        config = AppConfig.load()
    except RuntimeError as exc:
        print(f"[Erro] {exc}")
        return 1

    logger = setup_logging()
    build_system_prompt(config.confidence_threshold)
    graph = build_graph(config, logger, checkpointer=InMemorySaver())

    if args.pergunta:
        run_single_question(graph, args.pergunta.strip(), logger=logger, thread_id=args.thread_id)
    else:
        run_demo(graph, logger=logger)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
