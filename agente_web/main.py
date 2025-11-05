"""CLI entry point for the agente_web workflow."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from langchain_core.messages import HumanMessage

from agente_web.config import AppConfig, ConfigurationError, config
from agente_web.graph import create_app
from agente_web.state import GraphState

_REPORT_PATH = Path(__file__).resolve().parent / "smoke_test_output.txt"


def run_graph(question: str, *, app_config: AppConfig) -> GraphState:
    """Execute the compiled graph and return the final state."""

    app = create_app()
    initial_state: GraphState = {
        "messages": [HumanMessage(content=question)],
        "question": question,
        "warnings": [],
        "search_results": [],
    }
    invoke_config = {"configurable": {"thread_id": app_config.default_thread_id}}
    return app.invoke(initial_state, invoke_config)


def render_output(state: GraphState, question: str) -> str:
    """Render a user-friendly report string."""

    lines = [
        f"Pergunta: {question}",
        "",
        "Resumo:",
        state.get("summary") or "(vazio)",
        "",
        "Avisos:",
    ]

    warnings = state.get("warnings") or ["(nenhum)"]
    lines.extend(f"- {warning}" for warning in warnings)

    lines.append("")
    lines.append("Fontes:")
    results = state.get("search_results") or []
    if results:
        for item in results[:5]:
            title = item.get("title", "Sem título")
            url = item.get("url", "")
            lines.append(f"* {title} -> {url}")
    else:
        lines.append("(nenhuma)")

    return "\n".join(lines)


def _write_report(report: str) -> None:
    _REPORT_PATH.write_text(report, encoding="utf-8")


def main(argv: Optional[list[str]] = None) -> int:
    """Command-line interface for quick smoke tests."""

    args = list(argv or sys.argv[1:])
    question = " ".join(args).strip() or config.default_question

    try:
        final_state = run_graph(question, app_config=config)
    except ConfigurationError as exc:
        print(f"[agente_web] Configuração inválida: {exc}")
        return 2

    report = render_output(final_state, question)
    print(report)
    _write_report(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
