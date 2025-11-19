"""LangGraph nodes used by agente_tarefas."""
from __future__ import annotations

from copy import deepcopy
from typing import Callable, Dict, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from agente_tarefas.config import AppConfig, settings
from agente_tarefas.state import AgentState
from agente_tarefas.utils.prompts import (
    SYSTEM_PROMPT,
    build_round1_prompt,
    build_round2_prompt,
    build_round3_prompt,
)
from agente_tarefas.utils.rounds import build_initial_tasks, collect_new_tasks, select_completed_task, split_tasks
from agente_tarefas.utils.timeline import append_entry

NodeCallable = Callable[[AgentState], Dict[str, object]]


def resolve_app_config(config: AppConfig | None = None) -> AppConfig:
    """Return a usable AppConfig for node construction."""

    if config and hasattr(config, "create_llm") and hasattr(config, "create_checkpointer"):
        return config
    return settings


def _with_system_prompt(messages: List[BaseMessage]) -> List[BaseMessage]:
    if messages:
        return list(messages)
    return [SystemMessage(content=SYSTEM_PROMPT)]


def _invoke_llm(messages: List[BaseMessage], config: AppConfig) -> AIMessage:
    model = config.create_llm()
    return model.invoke(messages)


def _append_timeline_entry(
    timeline: List[dict],
    *,
    round_id: str,
    user_input: str,
    agent_response: str,
    notes: str | None = None,
) -> List[dict]:
    timeline_copy = list(timeline)
    append_entry(
        timeline_copy,
        round_id=round_id,  # type: ignore[arg-type]
        user_input=user_input,
        agent_response=agent_response,
        notes=notes,
    )
    return timeline_copy


def build_prepare_round1_node(config: AppConfig | None = None) -> NodeCallable:
    app_config = resolve_app_config(config)

    def _node(state: AgentState) -> Dict[str, object]:
        payload = state.get("round_payload", {})
        if payload.get("round") != "round1":
            return {}

        raw_tasks = payload.get("raw_tasks") or ""
        parsed_tasks = payload.get("tasks_list") or split_tasks(raw_tasks)
        tasks = build_initial_tasks(parsed_tasks)

        messages = _with_system_prompt(state.get("messages", []))
        messages.append(HumanMessage(content=build_round1_prompt(tasks)))
        response = _invoke_llm(messages, app_config)
        messages.append(response)

        timeline = _append_timeline_entry(
            state.get("timeline", []),
            round_id="round1",
            user_input=payload.get("user_input", raw_tasks),
            agent_response=response.content,
        )

        return {
            "tasks": tasks,
            "completed_ids": [],
            "duplicate_notes": [],
            "messages": messages,
            "timeline": timeline,
            "round_payload": {},
        }

    return _node


def build_complete_task_node(config: AppConfig | None = None) -> NodeCallable:
    app_config = resolve_app_config(config)

    def _node(state: AgentState) -> Dict[str, object]:
        payload = state.get("round_payload", {})
        if payload.get("round") != "round2":
            return {}

        selection_raw = str(payload.get("selected_id") or payload.get("user_input", ""))
        tasks = [dict(task) for task in state.get("tasks", [])]
        completed_ids = list(state.get("completed_ids", []))
        selection = select_completed_task(selection_raw, tasks, completed_ids)

        messages = _with_system_prompt(state.get("messages", []))
        messages.append(HumanMessage(content=build_round2_prompt(tasks, selection)))
        response = _invoke_llm(messages, app_config)
        messages.append(response)

        timeline = _append_timeline_entry(
            state.get("timeline", []),
            round_id="round2",
            user_input=payload.get("user_input", selection_raw),
            agent_response=response.content,
        )

        return {
            "tasks": tasks,
            "completed_ids": completed_ids,
            "messages": messages,
            "timeline": timeline,
            "round_payload": {},
        }

    return _node


def build_append_tasks_node(config: AppConfig | None = None) -> NodeCallable:
    app_config = resolve_app_config(config)

    def _node(state: AgentState) -> Dict[str, object]:
        payload = state.get("round_payload", {})
        if payload.get("round") != "round3":
            return {}

        entries: List[str] = payload.get("entries", [])
        duplicate_decisions = payload.get("duplicate_decisions", [])
        decision_map = {item["task"].casefold(): item["keep"] for item in duplicate_decisions}

        def _confirm_keep(item: str) -> bool:
            return decision_map.get(item.casefold(), True)

        tasks = [dict(task) for task in state.get("tasks", [])]
        duplicate_notes = list(state.get("duplicate_notes", []))
        previous_notes_len = len(duplicate_notes)

        if entries:
            collect_new_tasks(
                entries,
                tasks,
                duplicate_notes,
                confirm_keep_fn=_confirm_keep,
            )

        messages = _with_system_prompt(state.get("messages", []))
        messages.append(HumanMessage(content=build_round3_prompt(tasks, duplicate_notes)))
        response = _invoke_llm(messages, app_config)
        messages.append(response)

        new_notes = duplicate_notes[previous_notes_len:]
        notes_str = "; ".join(new_notes) if new_notes else None
        timeline = _append_timeline_entry(
            state.get("timeline", []),
            round_id="round3",
            user_input=payload.get("user_input", ""),
            agent_response=response.content,
            notes=notes_str,
        )

        return {
            "tasks": tasks,
            "duplicate_notes": duplicate_notes,
            "messages": messages,
            "timeline": timeline,
            "round_payload": {},
        }

    return _node


__all__ = [
    "build_prepare_round1_node",
    "build_complete_task_node",
    "build_append_tasks_node",
    "resolve_app_config",
    "NodeCallable",
]
