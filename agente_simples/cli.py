"""Command-line interface for the simple agent."""
from __future__ import annotations

from agente_simples.config import preflight_config_check
from agente_simples.graph import app
from agente_simples.state import DEFAULT_STATUS_ERROR
from agente_simples.utils.logging import get_logger

logger = get_logger(__name__)

EMPTY_MESSAGE = "Pergunta vazia. Tente novamente com mais detalhes."


def _handle_preflight() -> bool:
    """Run configuration checks and print actionable guidance."""

    checks = preflight_config_check()
    failures = [check for check in checks if check["result"] == "fail"]
    warnings = [check for check in checks if check["result"] == "warn"]

    for warning in warnings:
        print(f"⚠ {warning['message']}")

    if failures:
        for failure in failures:
            print(f"✗ {failure['message']}")
        logger.error("Falha de configuração | detalhes=%s", failures)
        return False

    return True


def _log_result(question: str, result: dict) -> None:
    status = result.get("status", "unknown")
    duration = result.get("duration_seconds")
    duration_fmt = f" duration={duration:.2f}s" if duration is not None else ""
    message = f"Pergunta='{question}' status={status}{duration_fmt}"

    if status == DEFAULT_STATUS_ERROR:
        logger.error("Execução concluída com erro controlado | %s", message)
    else:
        logger.info("Execução concluída com sucesso | %s", message)


def main() -> None:
    """Prompt for a question and display the agent response."""

    if not _handle_preflight():
        return

    question = input("Faça sua pergunta em português: ").strip()
    if not question:
        print(EMPTY_MESSAGE)
        return

    result = app.invoke({"messages": [{"role": "user", "content": question}]})
    answer = result.get("resposta", "Sem resposta disponível no momento.")

    _log_result(question, result)
    print(answer)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
