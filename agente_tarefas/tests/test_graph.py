from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from agente_tarefas.graph import create_graph
from agente_tarefas.state import AgentState


class DummyModel:
    def __init__(self):
        self.invocations = 0

    def invoke(self, messages):
        self.invocations += 1
        return AIMessage(content=f"resposta {self.invocations}")


class DummyConfig:
    def __init__(self):
        self._model = DummyModel()

    def create_llm(self):
        return self._model

    def create_checkpointer(self):
        return InMemorySaver()


def test_graph_invokes_model_and_appends_message():
    app = create_graph(DummyConfig())
    state: AgentState = {
        "messages": [HumanMessage(content="Teste")],
        "tasks": [],
        "completed_ids": [],
        "timeline": [],
    }

    result = app.invoke(state, config={"configurable": {"thread_id": "test"}})
    assert result["messages"][-1].content == "resposta 1"
