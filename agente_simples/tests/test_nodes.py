import pytest

from agente_simples.state import GraphState


class DummyLLM:
    def __init__(self, response: str):
        self._response = response

    def invoke(self, prompt: str):
        """Return a static result mimicking an LLM response."""
        class _Result:
            content = ""

        result = _Result()
        result.content = self._response
        return result


def test_validate_question_node_returns_metadata(monkeypatch):
    """Validation node must capture normalized question metadata and status."""
    from agente_simples.utils import nodes
    state: GraphState = {
        "messages": [{"role": "user", "content": "Qual é a capital do Brasil?"}],
        "status": "pending",
    }

    updated = nodes.validate_question_node(state)

    assert updated["metadata"]["question"] == "Qual é a capital do Brasil?"
    assert updated["status"] == "validated"


def test_invoke_model_node_returns_response(monkeypatch):
    """Model invocation should store the LLM response and update status."""
    from agente_simples.utils import nodes

    def _fake_llm_factory():
        return DummyLLM("Brasília é a capital do Brasil.")

    monkeypatch.setattr(nodes, "config", type("Cfg", (), {"create_llm": staticmethod(_fake_llm_factory)}))

    state: GraphState = {
        "metadata": {"question": "Qual é a capital do Brasil?"},
        "messages": [{"role": "user", "content": "Qual é a capital do Brasil?"}],
    }

    updated = nodes.invoke_model_node(state)

    assert updated["resposta"] == "Brasília é a capital do Brasil."
    assert updated["status"] == "responded"


def test_format_answer_node_formats_output():
    """Formatting node must wrap the response and set completion status."""
    from agente_simples.utils import nodes

    state: GraphState = {"resposta": "Brasília é a capital do Brasil."}

    updated = nodes.format_answer_node(state)

    assert updated["resposta"].startswith("Resposta do agente:")
    assert updated["status"] == "completed"
