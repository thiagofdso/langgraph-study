"""Unit tests for agente_web node helpers."""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agente_web.state import GraphState
from agente_web.utils.nodes import buscar, resumir


class DummyToolRunner:
    """Minimal stub mimicking ToolNode.invoke without external APIs."""

    def __init__(self, response: Dict[str, Any] | Exception):
        self._response = response
        self.calls: List[Any] = []

    def invoke(self, tool_calls: List[Dict[str, Any]]):
        self.calls.append(tool_calls)
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


class DummyLLM:
    """Stub that returns a customizable content payload."""

    def __init__(self, content: Any):
        self._content = content
        self.calls: List[Any] = []

    def invoke(self, messages: List[Any]):
        self.calls.append(messages)
        return type("Response", (), {"content": self._content})()


def _build_tool_response(results: List[Dict[str, Any]], *, call_id: str = "call-1"):
    payload = {"results": results}
    return {
        "messages": [
            ToolMessage(
                content=json.dumps(payload),
                name="tavily_search",
                tool_call_id=call_id,
            )
        ]
    }


def test_buscar_returns_warning_when_no_question():
    state: GraphState = {"messages": []}
    runner = DummyToolRunner(_build_tool_response([]))

    update = buscar(
        state,
        tool_runner=runner,
        tool_name="tavily_search",
        max_results=3,
    )

    assert update["question"] == ""
    assert update["search_results"] == []
    assert any("Pergunta ausente" in w for w in update["warnings"])
    assert runner.calls == []


def test_buscar_executes_tool_and_normalizes_results():
    messages = [HumanMessage(content="Como pesquisar arquivos no Linux?")]
    state: GraphState = {"messages": messages}
    results = [
        {"title": "Doc 1", "url": "https://doc1", "content": "Primeira dica"},
        {"title": "Doc 2", "url": "https://doc2", "snippet": "Segunda dica"},
        {"title": "Doc 3", "url": "https://doc3", "text": "Terceira dica"},
    ]
    runner = DummyToolRunner(_build_tool_response(results))

    update = buscar(
        state,
        tool_runner=runner,
        tool_name="tavily_search",
        max_results=2,
    )

    assert runner.calls and "Como pesquisar" in runner.calls[0][0]["args"]["query"]
    assert update["question"] == "Como pesquisar arquivos no Linux?"
    assert len(update["search_results"]) == 2  # limited by max_results
    assert update["metadata"]["result_count"] == 2
    assert "Poucos resultados" not in " ".join(update["warnings"])


def test_buscar_flags_few_results_warning():
    messages = [HumanMessage(content="Quais as novidades?")]
    runner = DummyToolRunner(
        _build_tool_response([{"title": "Única fonte", "url": "https://fonte", "content": "Resumo"}])
    )

    update = buscar(
        {"messages": messages},
        tool_runner=runner,
        tool_name="tavily_search",
        max_results=5,
    )

    assert update["metadata"]["result_count"] == 1
    assert any("Poucos resultados" in warning for warning in update["warnings"])


def test_buscar_handles_tool_errors():
    messages = [HumanMessage(content="Explique o comando find")]
    runner = DummyToolRunner(RuntimeError("falha Tavily"))

    update = buscar(
        {"messages": messages},
        tool_runner=runner,
        tool_name="tavily_search",
        max_results=5,
    )

    assert update["search_results"] == []
    assert any("Erro na busca" in warning for warning in update["warnings"])


def test_resumir_generates_summary_and_ai_message():
    state: GraphState = {
        "question": "Como pesquisar arquivos?",
        "search_results": [
            {"title": "Doc 1", "url": "https://doc1", "content": "Use find"},
            {"title": "Doc 2", "url": "https://doc2", "content": "Use locate"},
        ],
    }
    model = DummyLLM("Resumo final.")

    update = resumir(state, model=model, max_sources=2)

    assert update["summary"] == "Resumo final."
    assert isinstance(update["messages"][0], AIMessage)
    assert model.calls, "Model should have been invoked"


def test_resumir_handles_empty_results():
    update = resumir({"search_results": []}, model=DummyLLM("não deve chamar"))

    assert "Não foi possível gerar um resumo" in update["summary"]
    assert "messages" not in update


def test_resumir_handles_model_error():
    class FailingModel(DummyLLM):
        def invoke(self, messages: List[Any]):
            raise RuntimeError("falhou")

    update = resumir(
        {
            "question": "Explique find",
            "search_results": [{"title": "Doc", "url": "https://doc", "content": "Use find"}],
        },
        model=FailingModel(""),
        max_sources=1,
    )

    assert "erro na chamada" in update["summary"].lower()
    assert any("Erro ao gerar resumo" in warning for warning in update["warnings"])

