"""Command-line interface for the agente_tool project."""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, List, Optional

from langchain_core.messages import HumanMessage

from agente_tool import create_app
from agente_tool.config import (
    AppConfig,
    preflight_config_check,
    config as default_config,
)
from agente_tool.utils.logging import get_logger

logger = get_logger(__name__)
EMPTY_QUESTION_MESSAGE = "Pergunta vazia. Informe uma operação matemática completa."


def _print_checks(checks: Iterable[dict]) -> bool:
    """Render configuration check results and return success flag."""

    failures = [check for check in checks if check["result"] == "fail"]
    warnings = [check for check in checks if check["result"] == "warn"]

    for warning in warnings:
        print(f"⚠ {warning['message']}")

    if failures:
        for failure in failures:
            print(f"✗ {failure['message']}")
        logger.error("Falhas de configuração detectadas | detalhes=%s", failures)
        return False

    return True


def _log_result(question: str, result: dict) -> None:
    """Log summary about the CLI execution."""

    status = result.get("status", "unknown")
    duration = result.get("duration_seconds")
    duration_fragment = (
        f" duration={duration:.2f}s" if isinstance(duration, (int, float)) else ""
    )
    logger.info(
        "Execução concluída | pergunta='%s' status=%s%s",
        question,
        status,
        duration_fragment,
    )


def _handle_run(question: str, thread_id: Optional[str], config: AppConfig) -> int:
    """Execute the graph using the provided question and thread identifier."""

    stripped = question.strip()
    if not stripped:
        print(EMPTY_QUESTION_MESSAGE)
        return 1

    checks = preflight_config_check()
    if not _print_checks(checks):
        return 1

    app = create_app()
    thread = thread_id or config.default_thread_id
    payload = {"messages": [HumanMessage(content=stripped)]}
    runnable_config = {"configurable": {"thread_id": thread}}

    result = app.invoke(payload, config=runnable_config)
    answer = result.get("resposta", "Sem resposta disponível no momento.")

    _log_result(stripped, result)
    print(answer)
    return 0


def _interactive_prompt(config: AppConfig) -> int:
    """Prompt the user for a question when no CLI arguments are provided."""

    question = input("Faça sua pergunta em português: ")
    return _handle_run(question, thread_id=None, config=config)


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the CLI."""

    parser = argparse.ArgumentParser(
        description="Ferramentas de linha de comando para o agente de cálculo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Executa o agente com uma pergunta.")
    run_parser.add_argument("question", help="Pergunta a ser respondida pelo agente.")
    run_parser.add_argument(
        "--thread-id",
        help="Identificador opcional da thread para reutilizar memória em execuções subsequentes.",
    )

    return parser


def main(argv: Optional[List[str]] = None, *, config: AppConfig | None = None) -> int:
    """Entry point for `python -m agente_tool`."""

    resolved_config = config or default_config
    raw_args = list(argv) if argv is not None else sys.argv[1:]

    if not raw_args:
        return _interactive_prompt(resolved_config)

    parser = build_parser()
    args = parser.parse_args(raw_args)

    if args.command == "run":
        return _handle_run(args.question, args.thread_id, resolved_config)

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover - executed via CLI
    raise SystemExit(main())
