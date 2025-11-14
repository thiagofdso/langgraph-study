from __future__ import annotations

from langchain_core.messages import HumanMessage

from agente_perguntas.utils.nodes import resume_with_human_response


def test_graph_answers_known_question(graph, thread_config) -> None:
    config = thread_config("auto-question")
    question = "Como altero minha senha?"
    for _ in graph.stream({"messages": [HumanMessage(content=question)]}, config=config):
        pass
    state = graph.get_state(config).values
    assert state["status"] == "respondido automaticamente"
    assert "senha" in state["notes"]


def test_graph_handles_human_escalation(graph, thread_config) -> None:
    config = thread_config("hitl-question")
    question = "Preciso falar com um humano"
    interrupt_payload = None
    for event in graph.stream({"messages": [HumanMessage(content=question)]}, config=config):
        interrupt_events = event.get("__interrupt__")
        if interrupt_events:
            interrupt_payload = interrupt_events[0].value
    assert interrupt_payload is not None
    final_state = resume_with_human_response(
        graph,
        config=config,
        message="Especialista retornará em breve.",
        notes="Ticket aberto",
    )
    assert final_state["status"] == "encaminhar para humano"
    assert final_state["answer"] == "Especialista retornará em breve."
    assert final_state["notes"] == "Ticket aberto"
