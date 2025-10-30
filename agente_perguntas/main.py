"""Executable entry point for the FAQ routing agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, List

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from agente_perguntas.prompt import (
    DEMO_QUESTIONS,
    build_system_prompt,
    get_faq_entries,
    rank_faq_by_similarity,
)

ESCALATION_MESSAGE = (
    "Não encontrei a resposta no FAQ. Encaminharei sua dúvida para um especialista humano."
)

CONFIDENCE_THRESHOLD = 0.7


class AgentState(TypedDict, total=False):
    question: str
    answer: str
    confidence: float
    status: str
    notes: str


@dataclass
class InteractionResult:
    question: str
    answer: str
    confidence: float
    status: str
    notes: str


def _evaluate_question(state: AgentState) -> AgentState:
    """Evaluate the incoming question against the FAQ and decide next step."""
    question = state.get("question", "").strip()
    ranked = rank_faq_by_similarity(question)
    best_entry, best_score = ranked[0]

    if best_score >= CONFIDENCE_THRESHOLD:
        return {
            "answer": best_entry["answer"],
            "confidence": best_score,
            "status": "respondido automaticamente",
            "notes": f"Correspondência: {best_entry['question']}",
        }

    payload = {
        "question": question,
        "best_match": best_entry["question"],
        "best_match_confidence": round(best_score, 2),
        "faq_reference": get_faq_entries(),
    }
    human_payload = interrupt(payload)

    human_message = human_payload.get("message", ESCALATION_MESSAGE)
    human_notes = human_payload.get("notes", "Aguardando atendimento humano.")
    return {
        "answer": human_message,
        "confidence": best_score,
        "status": "encaminhar para humano",
        "notes": human_notes,
    }


def build_graph() -> StateGraph[AgentState]:
    """Construct the LangGraph workflow with a single evaluation node."""
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("evaluate", _evaluate_question)
    graph_builder.add_edge(START, "evaluate")
    graph_builder.add_edge("evaluate", END)
    return graph_builder.compile(checkpointer=InMemorySaver())


def _resume_interrupt(
    graph: StateGraph[AgentState],
    config: dict[str, Any],
    *,
    message: str,
    notes: str,
) -> AgentState:
    """Resume the graph after a human escalation using supplied payload."""
    for _ in graph.stream(Command(resume={"message": message, "notes": notes}), config=config):
        pass
    return graph.get_state(config).values  # type: ignore[return-value]


def _run_question(
    graph: StateGraph[AgentState], question: str, thread_id: str
) -> InteractionResult:
    """Run the graph for a single question, handling interrupts automatically."""
    config = {"configurable": {"thread_id": thread_id}}

    interrupt_payload: dict[str, Any] | None = None
    for event in graph.stream({"question": question}, config=config):
        interrupt_events = event.get("__interrupt__")
        if interrupt_events:
            interrupt_payload = interrupt_events[0].value  # type: ignore[index]

    state = graph.get_state(config)
    if interrupt_payload is not None:
        payload = interrupt_payload
        print("-" * 72)
        print("Encaminhar para humano:")
        print(f"Pergunta: {payload.get('question', question)}")
        print(
            "Melhor correspondência (confiança"
            f" {payload.get('best_match_confidence', 0):.2f}):"
            f" {payload.get('best_match')}"
        )
        human_message = input("Resposta do especialista (enter para padrão): ").strip()
        human_notes = input("Notas do especialista (opcional): ").strip()
        if not human_message:
            human_message = ESCALATION_MESSAGE
        if not human_notes:
            human_notes = "Encaminhamento registrado manualmente."
        final_values = _resume_interrupt(
            graph,
            config,
            message=human_message,
            notes=human_notes,
        )
    else:
        final_values = state.values

    return InteractionResult(
        question=question,
        answer=str(final_values.get("answer", "")),
        confidence=float(final_values.get("confidence", 0.0)),
        status=str(final_values.get("status", "desconhecido")),
        notes=str(final_values.get("notes", "")),
    )


def run_demo(graph: StateGraph[AgentState]) -> None:
    """Execute the scripted three-question demo and print results."""
    print("=== FAQ Routing Demo ===")
    print(f"Limite de confiança: {CONFIDENCE_THRESHOLD:.0%}\n")

    interactions: List[InteractionResult] = []
    for index, question in enumerate(DEMO_QUESTIONS, start=1):
        result = _run_question(graph, question, thread_id=f"demo-{index}")
        interactions.append(result)
        print("Pergunta:", result.question)
        print(f"Status: {result.status} (confiança {result.confidence:.2f})")
        print("Resposta:", result.answer)
        if result.notes:
            print("Notas:", result.notes)
        print()

    resolved = [item for item in interactions if item.status == "respondido automaticamente"]
    escalated = [item for item in interactions if item.status == "encaminhar para humano"]

    print("Resumo final")
    print("-" * 40)
    print("Respondidos automaticamente:")
    for item in resolved:
        print(f"• {item.question} (confiança {item.confidence:.2f})")

    print("\nEncaminhar para humano:")
    if escalated:
        for item in escalated:
            print(f"• {item.question} (confiança {item.confidence:.2f})")
    else:
        print("• Nenhuma pergunta pendente")


def main() -> None:
    """Prepare prompt, build graph, and execute scripted demo."""
    _ = build_system_prompt(CONFIDENCE_THRESHOLD)
    if not os.environ.get("GEMINI_API_KEY"):
        print("[Aviso] Defina GEMINI_API_KEY para chamar o modelo Gemini.")
    graph = build_graph()
    run_demo(graph)


if __name__ == "__main__":
    main()
