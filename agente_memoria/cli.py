
"""Command-line interface for the memory agent."""
from __future__ import annotations

import argparse

import uuid

from agente_memoria.config import config, preflight_config_check
from agente_memoria.graph import create_app
from agente_memoria.state import GraphState
from agente_memoria.utils.logging import get_logger

logger = get_logger(__name__)

EMPTY_MESSAGE = "Pergunta vazia. Por favor, forneça mais detalhes."

def _handle_preflight() -> bool:
    """Run configuration checks and print actionable guidance."""
    checks = preflight_config_check()
    failures = [check for check in checks if check["result"] == "fail"]
    warnings = [check for check in checks if check["result"] == "warn"]

    for warning in warnings:
        print(f"?? {warning['message']}")

    if failures:
        for failure in failures:
            print(f"? {failure['message']}")
        logger.error("Falha na configuração | detalhes=%s", failures)
        return False

    return True

def main() -> None:
    """Main loop for the memory agent CLI."""
    if not _handle_preflight():
        return

    parser = argparse.ArgumentParser(description="Memory Agent CLI")
    parser.add_argument("--check", action="store_true", help="Run preflight checks and exit")
    parser.add_argument("--thread", type=str, default=config.default_thread_id, help="Conversation thread ID")
    args = parser.parse_args()

    if args.check:
        if _handle_preflight():
            print("Verificações iniciais aprovadas.")
        return

    thread_id = args.thread
    app = create_app()

    while True:
        question = input(f"[{thread_id}] Faça sua pergunta (ou digite /sair ou /reset para limpar a memoria): ").strip()

        if not question:
            print(EMPTY_MESSAGE)
            continue

        if question.lower() == "/sair":
            break

        if question.lower() == "/reset":
            thread_id = str(uuid.uuid4())
            print(f"Histórico resetado. Novo tópico de conversa: '{thread_id}'.")
            continue
        
        config_ = {"configurable": {"thread_id": thread_id}}
        state = GraphState(messages=[("user", question)], thread_id=thread_id)
        result = app.invoke(state, config=config_)

        answer = result.get("resposta", "Nenhuma resposta disponível no momento.")
        print(answer)
if __name__ == "__main__":
    main()
