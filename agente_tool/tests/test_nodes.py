"""Unit tests for agente_tool node utilities."""

from __future__ import annotations

import logging
import time
from typing import Dict

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agente_tool.config import AppConfig
from agente_tool.state import GraphState
from agente_tool.tests.conftest import DummyLLM
from agente_tool.utils import (
    STATUS_COMPLETED,
    STATUS_ERROR,
    STATUS_RESPONDED,
    STATUS_VALIDATED,
    handle_tool_result,
    finalize_response,
    format_response,
    invoke_model,
    plan_tool_usage,
    validate_input,
)


def _apply_update(state: GraphState, update: Dict) -> GraphState:
    """Utility to merge node updates mimicking LangGraph behavior."""

    new_state = dict(state)
    if "messages" in update:
        existing = list(state.get("messages", []))
        existing.extend(update["messages"])
        new_state["messages"] = existing
    for key, value in update.items():
        if key == "messages":
            continue
        new_state[key] = value
    return new_state


def test_validate_input_rejects_short_question():
    state: GraphState = {"messages": [HumanMessage(content="Oi")], "metadata": {}}
    update = validate_input(state)

    assert update["status"] == STATUS_ERROR
    assert "Preciso de mais detalhes" in update["resposta"]


def test_validate_input_accepts_question(initial_state):
    update = validate_input(initial_state)
    merged = _apply_update(initial_state, update)

    assert update["status"] == STATUS_VALIDATED
    assert "system_prompt" in update["metadata"]
    assert merged["metadata"]["question"].startswith("quanto é")


def test_plan_tool_usage_extracts_expression(initial_state):
    validated = _apply_update(initial_state, validate_input(initial_state))
    ai_message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {"expression": "300 / 4"},
                "id": "call_1",
            }
        ],
    )
    with_response = _apply_update(validated, {"messages": [ai_message]})
    update = plan_tool_usage(with_response)

    assert update["selected_tool"] == "calculator"
    assert update["tool_plan"]["args"]["expression"] == "300 / 4"
    assert update["tool_plan"]["call_id"] == "call_1"
    assert update["pending_tool_calls"][0]["args"]["expression"] == "300 / 4"
    assert update["pending_tool_calls"][0]["call_id"] == "call_1"


def test_plan_tool_usage_handles_non_math_question():
    state: GraphState = {
        "messages": [HumanMessage(content="Qual é a capital do Brasil?")],
        "metadata": {},
    }
    validated = _apply_update(state, validate_input(state))
    ai_message = AIMessage(content="A capital do Brasil é Brasília.")
    with_response = _apply_update(validated, {"messages": [ai_message]})
    update = plan_tool_usage(with_response)

    assert update["tool_plan"] is None
    assert update["selected_tool"] is None
    assert update["pending_tool_calls"] == []


def test_handle_tool_result_updates_state():
    plan_state: GraphState = {
        "metadata": {"question": "quanto é 300 dividido por 4?", "system_prompt": ""},
        "tool_plan": {
            "name": "calculator",
            "args": {"expression": "300 / 4"},
            "call_id": "call_1",
        },
        "messages": [
            ToolMessage(tool_call_id="call_1", name="calculator", content="75.0")
        ],
    }

    update = handle_tool_result(plan_state)

    assert update["status"] == STATUS_VALIDATED
    assert update["tool_call"]["result"] == "75.0"
    assert update["metadata"]["last_tool_expression"] == "300 / 4"
    assert update["pending_tool_calls"] == []


def test_handle_tool_result_handles_error():
    plan_state: GraphState = {
        "metadata": {},
        "tool_plan": {
            "name": "calculator",
            "args": {"expression": "1 / 0"},
            "call_id": "call_2",
        },
        "messages": [
            ToolMessage(
                tool_call_id="call_2",
                name="calculator",
                content="Error: division by zero",
            )
        ],
    }

    update = handle_tool_result(plan_state)

    assert update["status"] == STATUS_ERROR
    assert "Revise a operação" in update["resposta"]
    assert update["tool_call"]["error"].startswith("Error:")


def test_handle_tool_result_without_tool_message():
    plan_state: GraphState = {
        "metadata": {},
        "tool_plan": {
            "name": "calculator",
            "args": {"expression": "2 + 2"},
            "call_id": "call_3",
        },
        "messages": [],
    }

    update = handle_tool_result(plan_state)

    assert update["status"] == STATUS_ERROR


def test_invoke_model_with_dummy_llm(initial_state):
    validated = _apply_update(initial_state, validate_input(initial_state))
    llm = DummyLLM("Estou pronto para ajudar com cálculos.")
    update = invoke_model(validated, llm=llm)

    assert update["status"] == STATUS_RESPONDED
    assert "pronto para ajudar" in update["resposta"]


def test_invoke_model_handles_list_content(initial_state):
    validated = _apply_update(initial_state, validate_input(initial_state))
    content = [{"text": "Resultado parcial"}, {"text": " confirmado."}]
    llm = DummyLLM(AIMessage(content=content))

    update = invoke_model(validated, llm=llm)

    assert update["status"] == STATUS_RESPONDED
    assert "Resultado parcial" in update["resposta"]


def test_invoke_model_without_question_returns_error():
    state: GraphState = {"messages": [], "metadata": {}}
    update = invoke_model(
        state, llm=DummyLLM("irrelevante"), app_config=AppConfig(api_key="fake")
    )

    assert update["status"] == STATUS_ERROR


def test_invoke_model_without_api_key_reports_error(initial_state):
    validated = _apply_update(initial_state, validate_input(initial_state))
    state = dict(validated)

    update = invoke_model(state, llm=None, app_config=AppConfig(api_key=None))

    assert update["status"] == STATUS_ERROR


def test_format_response_success_path():
    start_time = time.perf_counter() - 0.5
    state: GraphState = {
        "resposta": "O resultado é 75",
        "status": STATUS_RESPONDED,
        "metadata": {"started_at": start_time},
    }

    update = format_response(state)

    assert update["status"] == STATUS_COMPLETED
    assert update["resposta"].startswith("Resposta do agente:")
    assert update["duration_seconds"] > 0


def test_format_response_error_path():
    state: GraphState = {
        "resposta": "Não foi possível processar",
        "status": STATUS_ERROR,
        "metadata": {"started_at": time.perf_counter()},
    }

    update = format_response(state)

    assert update["status"] == STATUS_ERROR
    assert update["resposta"].startswith("Resposta do agente:")


def test_validate_input_logs_warning(caplog):
    caplog.set_level(logging.WARNING)
    state: GraphState = {"messages": [HumanMessage(content="Oi")], "metadata": {}}

    validate_input(state)

    assert any("Pergunta inválida" in record.message for record in caplog.records)


def test_finalize_response_after_tool(initial_state):
    validated = _apply_update(initial_state, validate_input(initial_state))
    tool_call_msg = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator",
                "args": {"expression": "300 / 4"},
                "id": "call_1",
            }
        ],
    )
    state_after_model = _apply_update(
        validated, {"messages": [tool_call_msg], "status": STATUS_RESPONDED}
    )
    plan_update = plan_tool_usage(state_after_model)
    planned_state = _apply_update(state_after_model, plan_update)
    tool_state = _apply_update(
        planned_state,
        {
            "messages": [
                ToolMessage(tool_call_id="call_1", name="calculator", content="75.0")
            ]
        },
    )
    handled_state = _apply_update(tool_state, handle_tool_result(tool_state))

    llm = DummyLLM("Resultado final: 75.")
    update = finalize_response(handled_state, llm=llm)

    assert update["status"] == STATUS_RESPONDED
    assert "75" in update["resposta"]
