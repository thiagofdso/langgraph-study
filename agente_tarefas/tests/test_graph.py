from dataclasses import dataclass

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agente_tarefas.graph import create_graph
from agente_tarefas.state import AgentState, state_factory


@dataclass
class DummyModel:
    responses: list[str]

    def __post_init__(self) -> None:
        self._cursor = 0

    def invoke(self, messages):  # pragma: no cover - deterministic helper
        _ = messages
        response_text = self.responses[self._cursor]
        self._cursor = min(self._cursor + 1, len(self.responses) - 1)
        return AIMessage(content=response_text)


class DummyConfig:
    def __init__(self, responses=None):
        if responses is None:
            responses = ['[{"op":"add","tasks":["Estudar"]},{"op":"del","tasks":["ler"]}]']
        self._model = DummyModel(responses)

    def create_llm(self):
        return self._model

    def create_checkpointer(self):
        return InMemorySaver()


def test_graph_updates_tasks_and_summarizes():
    app = create_graph(DummyConfig())
    state: AgentState = state_factory.build(messages=[HumanMessage(content="Adicione estudar e remova ler")])
    state["tasks"] = ["Ler"]

    result = app.invoke(state, config={"configurable": {"thread_id": "test"}})

    assert "Estudar" in result["tasks"]
    assert all(task.casefold() != "ler" for task in result["tasks"])
    final_message = result["messages"][-1]
    assert isinstance(final_message, AIMessage)
    assert "Tarefas removidas" in final_message.content
    assert "- Estudar" in final_message.content
    assert "Lista atual" in final_message.content


def test_graph_handles_invalid_payload():
    app = create_graph(DummyConfig(responses=["nao eh json"]))
    state: AgentState = state_factory.build(messages=[HumanMessage(content="Remova tudo")])
    state["tasks"] = ["Estudar"]

    result = app.invoke(state, config={"configurable": {"thread_id": "test"}})

    assert result["tasks"] == ["Estudar"]
    final_message = result["messages"][-1]
    assert isinstance(final_message, AIMessage)
    assert "Nenhuma alteração foi aplicada" in final_message.content
