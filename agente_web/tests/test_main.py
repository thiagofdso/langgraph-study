"""Integration tests for agente_web.main helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from langchain_core.messages import HumanMessage

from agente_web import main as main_module


class DummyGraph:
    def __init__(self, return_state: Dict[str, Any]):
        self.return_state = return_state
        self.invocations: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    def invoke(self, state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        self.invocations.append((state, config))
        return self.return_state


def test_run_graph_builds_human_message_and_thread_id(monkeypatch):
    graph = DummyGraph({"summary": "ok"})
    monkeypatch.setattr(main_module, "create_app", lambda: graph)

    result = main_module.run_graph(
        "Qual a capital do Brasil?", app_config=main_module.config
    )

    assert result["summary"] == "ok"
    assert graph.invocations, "Graph should have been invoked exactly once."
    state, invoke_config = graph.invocations[0]

    assert isinstance(state["messages"][0], HumanMessage)
    assert state["messages"][0].content == "Qual a capital do Brasil?"
    assert invoke_config["configurable"]["thread_id"] == main_module.config.default_thread_id
