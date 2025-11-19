"""Command-line runner for the three-round task agent."""
from __future__ import annotations

from typing import Callable, Dict, List

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agente_tarefas.config import ConfigurationError, preflight_config_check, settings
from agente_tarefas.graph import create_graph
from agente_tarefas.state import AgentState, TaskItem, state_factory
from agente_tarefas.utils.prompts import SYSTEM_PROMPT
from agente_tarefas.utils.rounds import (
    ConfirmationFunc,
    select_completed_task,
    split_tasks,
)

PromptFn = Callable[[str], str]
OutputFn = Callable[[str], None]


def _handle_preflight(output_fn: OutputFn) -> bool:
    """Run simple configuration diagnostics."""

    failures = [item for item in preflight_config_check() if item["result"] == "fail"]
    for failure in failures:
        output_fn(f"✗ {failure['message']}")
    return not failures


def _invoke_agent(app, *, thread_id: str, state: AgentState) -> AgentState:
    """Invoke the LangGraph application with the provided state."""

    config = {"configurable": {"thread_id": thread_id}}
    return app.invoke(state, config=config)


def _request_confirmation(question: str, input_fn: PromptFn, output_fn: OutputFn) -> bool:
    answer = input_fn(question).strip().lower()
    output_fn(f"Usuário: {answer}")
    return answer in {"s", "sim"}


def _round_one(input_fn: PromptFn, output_fn: OutputFn) -> tuple[str, List[str]]:
    """Collect and validate the initial task list from the user."""

    while True:
        user_entry = input_fn(
            "Rodada 1 – informe tarefas separadas por vírgula (ex.: Estudar, Lavar louça): "
        ).strip()
        output_fn(f"Usuário: {user_entry}")
        parsed = split_tasks(user_entry)
        if not parsed:
            output_fn("Agente: Preciso de pelo menos uma tarefa. Digite novamente por favor.")
            continue
        return user_entry, parsed


def _round_two(
    tasks_state: List[TaskItem],
    completed_ids: List[int],
    input_fn: PromptFn,
    output_fn: OutputFn,
) -> int:
    while True:
        selection_raw = input_fn("Rodada 2 – informe o número da tarefa concluída: ").strip()
        output_fn(f"Usuário: {selection_raw}")
        try:
            temp_tasks = [dict(task) for task in tasks_state]
            temp_completed = list(completed_ids)
            return select_completed_task(selection_raw, temp_tasks, temp_completed)
        except ValueError as error:
            output_fn(f"Agente: {error}")


def _round_three(
    tasks_state: List[TaskItem],
    input_fn: PromptFn,
    output_fn: OutputFn,
) -> tuple[str, List[str], List[Dict[str, bool]]]:
    """Collect optional tasks for round 3 plus duplicate decisions."""

    while True:
        user_entry = input_fn(
            "Rodada 3 – adicione novas tarefas separadas por vírgula (ou Enter para finalizar): "
        ).strip()
        output_fn(f"Usuário: {user_entry}")
        if not user_entry:
            if _request_confirmation(
                "Confirmar finalização sem novas tarefas? (s/n): ", input_fn, output_fn
            ):
                return "Nenhuma tarefa adicionada", [], []
            output_fn("Agente: Sem problemas, você pode informar novas tarefas agora.")
            continue

        parsed = split_tasks(user_entry)
        if not parsed:
            output_fn("Agente: As entradas estavam vazias após limpeza. Tente novamente.")
            continue

        duplicate_decisions: List[Dict[str, bool]] = []
        existing_descriptions = {task["description"].casefold() for task in tasks_state}
        kept_items: List[str] = []

        for item in parsed:
            lowered = item.casefold()
            if lowered in existing_descriptions:
                keep = _request_confirmation(
                    f"A tarefa '{item}' já existe. Deseja mantê-la duplicada? (s/n): ", input_fn, output_fn
                )
                duplicate_decisions.append({"task": item, "keep": keep})
                if not keep:
                    continue
            kept_items.append(item)

        if not kept_items:
            output_fn(
                "Agente: Nenhuma nova tarefa foi adicionada. Você pode tentar novamente ou finalizar."
            )
            continue

        return ", ".join(kept_items), parsed, duplicate_decisions


def run_cli(*, input_fn: PromptFn = input, output_fn: OutputFn = print) -> None:
    """Execute the three-round interactive experience."""

    if not _handle_preflight(output_fn):
        return

    try:
        app = create_graph(settings)
    except ConfigurationError as error:
        output_fn(f"✗ {error}")
        return

    thread_id = settings.build_thread_id()
    agent_state: AgentState = state_factory.build(
        messages=[SystemMessage(content=SYSTEM_PROMPT)]
    )

    # Round 1
    user_text_round1, parsed_round1 = _round_one(input_fn, output_fn)
    agent_state["round_payload"] = {
        "round": "round1",
        "user_input": user_text_round1,
        "raw_tasks": user_text_round1,
        "tasks_list": parsed_round1,
    }
    agent_state = _invoke_agent(app, thread_id=thread_id, state=agent_state)
    agent_reply_round1 = agent_state["messages"][-1].content
    output_fn(f"Agente: {agent_reply_round1}")

    # Round 2
    selected_task = _round_two(agent_state["tasks"], agent_state["completed_ids"], input_fn, output_fn)
    agent_state["round_payload"] = {
        "round": "round2",
        "user_input": str(selected_task),
        "selected_id": selected_task,
    }
    agent_state = _invoke_agent(app, thread_id=thread_id, state=agent_state)
    agent_reply_round2 = agent_state["messages"][-1].content
    output_fn(f"Agente: {agent_reply_round2}")

    # Round 3
    summary_round3, entries_round3, duplicate_decisions = _round_three(
        agent_state["tasks"], input_fn, output_fn
    )
    agent_state["round_payload"] = {
        "round": "round3",
        "user_input": summary_round3,
        "entries": entries_round3,
        "duplicate_decisions": duplicate_decisions,
    }
    agent_state = _invoke_agent(app, thread_id=thread_id, state=agent_state)
    agent_reply_round3 = agent_state["messages"][-1].content
    output_fn(f"Agente: {agent_reply_round3}")


def main() -> None:  # pragma: no cover - CLI entry point
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nAgente: Sessão interrompida pelo usuário.")


if __name__ == "__main__":  # pragma: no cover
    main()
