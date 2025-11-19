"""Command-line runner for the three-round task agent."""
from __future__ import annotations

from typing import Callable, List, Sequence

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from agente_tarefas.config import ConfigurationError, preflight_config_check, settings
from agente_tarefas.graph import create_graph
from agente_tarefas.state import AgentState, TaskItem, TimelineEntry
from agente_tarefas.utils.prompts import (
    SYSTEM_PROMPT,
    build_round1_prompt,
    build_round2_prompt,
    build_round3_prompt,
)
from agente_tarefas.utils.rounds import (
    ConfirmationFunc,
    build_initial_tasks,
    collect_new_tasks,
    select_completed_task,
    split_tasks,
)
from agente_tarefas.utils.timeline import append_entry

PromptFn = Callable[[str], str]
OutputFn = Callable[[str], None]


def _handle_preflight(output_fn: OutputFn) -> bool:
    """Run simple configuration diagnostics."""

    failures = [item for item in preflight_config_check() if item["result"] == "fail"]
    for failure in failures:
        output_fn(f"✗ {failure['message']}")
    return not failures


def _invoke_agent(
    app,
    *,
    thread_id: str,
    messages: Sequence[BaseMessage],
    tasks: List[TaskItem],
    completed_ids: List[int],
    timeline: List[TimelineEntry],
) -> AgentState:
    config = {"configurable": {"thread_id": thread_id}}
    payload: AgentState = {
        "messages": list(messages),
        "tasks": tasks,
        "completed_ids": completed_ids,
        "timeline": timeline,
    }
    return app.invoke(payload, config=config)


def _request_confirmation(question: str, input_fn: PromptFn, output_fn: OutputFn) -> bool:
    answer = input_fn(question).strip().lower()
    output_fn(f"Usuário: {answer}")
    return answer in {"s", "sim"}


def _round_one(tasks_state: List[TaskItem], input_fn: PromptFn, output_fn: OutputFn) -> str:
    while True:
        user_entry = input_fn(
            "Rodada 1 – informe tarefas separadas por vírgula (ex.: Estudar, Lavar louça): "
        ).strip()
        output_fn(f"Usuário: {user_entry}")
        parsed = split_tasks(user_entry)
        if not parsed:
            output_fn("Agente: Preciso de pelo menos uma tarefa. Digite novamente por favor.")
            continue
        tasks_state.clear()
        tasks_state.extend(build_initial_tasks(parsed))
        return user_entry


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
            return select_completed_task(selection_raw, tasks_state, completed_ids)
        except ValueError as error:
            output_fn(f"Agente: {error}")


def _round_three(
    tasks_state: List[TaskItem],
    duplicate_notes: List[str],
    input_fn: PromptFn,
    output_fn: OutputFn,
) -> str:
    def _duplicate_prompt(item: str) -> bool:
        return _request_confirmation(
            f"A tarefa '{item}' já existe. Deseja mantê-la duplicada? (s/n): ", input_fn, output_fn
        )

    while True:
        user_entry = input_fn(
            "Rodada 3 – adicione novas tarefas separadas por vírgula (ou Enter para finalizar): "
        ).strip()
        output_fn(f"Usuário: {user_entry}")
        if not user_entry:
            if _request_confirmation(
                "Confirmar finalização sem novas tarefas? (s/n): ", input_fn, output_fn
            ):
                return "Nenhuma tarefa adicionada"
            output_fn("Agente: Sem problemas, você pode informar novas tarefas agora.")
            continue
        parsed = split_tasks(user_entry)
        if not parsed:
            output_fn("Agente: As entradas estavam vazias após limpeza. Tente novamente.")
            continue
        added = collect_new_tasks(parsed, tasks_state, duplicate_notes, confirm_keep_fn=_duplicate_prompt)
        if not added:
            output_fn(
                "Agente: Nenhuma nova tarefa foi adicionada. Você pode tentar novamente ou finalizar."
            )
            continue
        return ", ".join(added)


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
    tasks_state: List[TaskItem] = []
    completed_ids: List[int] = []
    timeline: List[TimelineEntry] = []
    duplicate_notes: List[str] = []

    # Round 1
    user_text_round1 = _round_one(tasks_state, input_fn, output_fn)
    state_round1: Sequence[BaseMessage] = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=build_round1_prompt(tasks_state)),
    ]
    result_round1 = _invoke_agent(
        app,
        thread_id=thread_id,
        messages=state_round1,
        tasks=tasks_state,
        completed_ids=completed_ids,
        timeline=timeline,
    )
    agent_reply_round1 = result_round1["messages"][-1].content
    output_fn(f"Agente: {agent_reply_round1}")
    append_entry(
        timeline,
        round_id="round1",
        user_input=user_text_round1,
        agent_response=agent_reply_round1,
    )

    # Round 2
    selected_task = _round_two(tasks_state, completed_ids, input_fn, output_fn)
    state_round2 = [HumanMessage(content=build_round2_prompt(tasks_state, selected_task))]
    result_round2 = _invoke_agent(
        app,
        thread_id=thread_id,
        messages=state_round2,
        tasks=tasks_state,
        completed_ids=completed_ids,
        timeline=timeline,
    )
    agent_reply_round2 = result_round2["messages"][-1].content
    output_fn(f"Agente: {agent_reply_round2}")
    append_entry(
        timeline,
        round_id="round2",
        user_input=str(selected_task),
        agent_response=agent_reply_round2,
    )

    # Round 3
    round3_summary = _round_three(tasks_state, duplicate_notes, input_fn, output_fn)
    state_round3 = [HumanMessage(content=build_round3_prompt(tasks_state, duplicate_notes))]
    result_round3 = _invoke_agent(
        app,
        thread_id=thread_id,
        messages=state_round3,
        tasks=tasks_state,
        completed_ids=completed_ids,
        timeline=timeline,
    )
    agent_reply_round3 = result_round3["messages"][-1].content
    output_fn(f"Agente: {agent_reply_round3}")
    append_entry(
        timeline,
        round_id="round3",
        user_input=round3_summary,
        agent_response=agent_reply_round3,
        notes="; ".join(duplicate_notes) if duplicate_notes else None,
    )


def main() -> None:  # pragma: no cover - CLI entry point
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\nAgente: Sessão interrompida pelo usuário.")


if __name__ == "__main__":  # pragma: no cover
    main()
