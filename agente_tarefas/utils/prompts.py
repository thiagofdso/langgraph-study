"""Prompt builders for the dynamic task agent."""
from __future__ import annotations

from typing import Sequence

SYSTEM_PROMPT = (
    "Você gerencia uma lista única de tarefas em português."
    " Sempre analise a última mensagem do usuário e converta o pedido em operações JSON"
    " que serão executadas por outro serviço. Não produza explicações em linguagem natural"
    " nessa etapa intermediária."
)

PROMPT_EXAMPLE = """\
Exemplos de operações esperadas (JSON):
- Apenas listar: [{"op":"listar"}]
- Adicionar duas tarefas: [{"op":"add","tasks":["estudar","fazer compras"]}]
- Adicionar e remover: [
  {"op":"add","tasks":["estudar"]},
  {"op":"del","tasks":["fazer compras"]}
]"""


def _render_tasks_snapshot(tasks: Sequence[str]) -> str:
    if not tasks:
        return "- (nenhuma tarefa registrada)"
    return "\n".join(f"- {item}" for item in tasks)


def build_operations_prompt(tasks: Sequence[str], user_message: str) -> str:
    """Create the LLM instruction asking for JSON operations."""

    snapshot = _render_tasks_snapshot(tasks)
    return (
        "Contexto atual:\n"
        f"{snapshot}\n\n"
        f"Mensagem do usuário: {user_message}\n\n"
        "Responda SOMENTE com um array JSON contendo objetos nesta ordem exata."
        " Campos obrigatórios:\n"
        "  - \"op\": \"listar\" | \"add\" | \"del\"\n"
        "  - \"tasks\": lista de textos apenas para operações \"add\" ou \"del\"\n"
        "Regras:\n"
        "  • Preserve a ordem natural descrita pelo usuário.\n"
        "  • Limpe espaços extras e remova duplicidade ignorando maiúsculas/minúsculas.\n"
        "  • Caso o usuário peça apenas para listar, responda exatamente com `[{\"op\":\"listar\"}]`.\n"
        "  • Se a instrução for ambígua, inclua apenas operações seguras (listar ou nenhuma alteração).\n\n"
        f"{PROMPT_EXAMPLE}"
    )


__all__ = ["SYSTEM_PROMPT", "build_operations_prompt"]
