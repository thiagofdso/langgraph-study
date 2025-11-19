"""Prompt builders shared across the CLI and graph."""
from __future__ import annotations

from typing import Iterable, List

from agente_tarefas.state import TaskItem

SYSTEM_PROMPT = (
    "Você é um assistente que atua em português brasileiro ajudando o usuário a gerenciar"
    " tarefas em uma sessão de três rodadas. Sempre responda de forma clara, curta e"
    " numerada quando solicitado, liste totais no encerramento e nunca faça mais perguntas"
    " após a terceira rodada. Use um tom encorajador e objetivo."
)


def build_round1_prompt(tasks: Iterable[TaskItem]) -> str:
    task_lines = "\n".join(f"{task['id']}. {task['description']}" for task in tasks)
    return (
        "Rodada 1: Confirmar tarefas recebidas.\n"
        "Liste cada tarefa numerada e incentive o usuário a continuar para a segunda rodada.\n"
        "Tarefas informadas:\n"
        f"{task_lines}"
    )


def build_round2_prompt(tasks: Iterable[TaskItem], completed_id: int) -> str:
    lines: List[str] = []
    for task in tasks:
        status = "concluída" if task["status"] == "completed" else "pendente"
        marker = "✅" if task["status"] == "completed" else "🕒"
        lines.append(f"{task['id']}. {task['description']} ({status}) {marker}")
    rendered = "\n".join(lines)
    return (
        "Rodada 2: Confirmar a tarefa marcada como concluída e orientar o usuário para a última rodada.\n"
        f"Tarefa concluída: {completed_id}.\n"
        "Situação atual das tarefas:\n"
        f"{rendered}"
    )


def build_round3_prompt(tasks: Iterable[TaskItem], duplicate_notes: List[str]) -> str:
    completed = [task for task in tasks if task["status"] == "completed"]
    pending = [task for task in tasks if task["status"] == "pending"]
    completed_lines = "\n".join(f"- {task['description']}" for task in completed) or "- (nenhuma)"
    pending_lines = "\n".join(f"- {task['description']}" for task in pending) or "- (nenhuma)"
    notes_section = "\n".join(f"- {note}" for note in duplicate_notes) or "- Nenhum aviso sobre duplicatas"
    return (
        "Rodada 3: Encerrar a sessão.\n"
        "Produza um resumo final destacando tarefas concluídas, tarefas pendentes e totais.\n"
        "Inclua orientações breves para reiniciar a sessão e registre decisões sobre duplicatas.\n"
        f"Tarefas concluídas:\n{completed_lines}\n"
        f"Tarefas pendentes:\n{pending_lines}\n"
        "Observações sobre duplicatas:\n"
        f"{notes_section}"
    )


__all__ = [
    "SYSTEM_PROMPT",
    "build_round1_prompt",
    "build_round2_prompt",
    "build_round3_prompt",
]
