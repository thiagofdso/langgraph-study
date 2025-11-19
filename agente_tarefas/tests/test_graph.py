from dataclasses import dataclass

from langchain_core.messages import AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver

from agente_tarefas.graph import create_graph
from agente_tarefas.state import AgentState, state_factory


@dataclass
class DummyModel:
    responses: list[str]

    def __post_init__(self) -> None:
        self._cursor = 0

    def invoke(self, messages):  # pragma: no cover - behavior is deterministic
        _ = messages
        response_text = self.responses[self._cursor]
        self._cursor = min(self._cursor + 1, len(self.responses) - 1)
        return AIMessage(content=response_text)


class DummyConfig:
    def __init__(self):
        self._model = DummyModel(["round1", "round2", "round3"])

    def create_llm(self):
        return self._model

    def create_checkpointer(self):
        return InMemorySaver()


def test_graph_processes_round1_payload():
    app = create_graph(DummyConfig())
    state: AgentState = state_factory.build(messages=[SystemMessage(content="sys")])
    state["round_payload"] = {
        "round": "round1",
        "user_input": "Estudar",
        "raw_tasks": "Estudar",
        "tasks_list": ["Estudar"],
    }

    result = app.invoke(state, config={"configurable": {"thread_id": "test"}})

    assert result["tasks"][0]["description"] == "Estudar"
    assert result["messages"][-1].content == "round1"
    assert result["timeline"][0]["round_id"] == "round1"


def test_graph_processes_round2_payload():
    app = create_graph(DummyConfig())
    state: AgentState = state_factory.build(messages=[SystemMessage(content="sys")])
    state["tasks"] = [
        {"id": 1, "description": "Estudar", "status": "pending", "source_round": "round1"}
    ]
    state["round_payload"] = {"round": "round2", "user_input": "1", "selected_id": 1}

    result = app.invoke(state, config={"configurable": {"thread_id": "test"}})

    assert result["completed_ids"] == [1]
    assert result["tasks"][0]["status"] == "completed"
