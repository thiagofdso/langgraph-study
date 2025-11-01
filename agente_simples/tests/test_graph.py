from unittest.mock import patch

import pytest

from agente_simples.state import GraphState


@pytest.fixture
def fake_llm():
    """Provide a fake LLM that records prompts for assertion purposes."""
    class _FakeLLM:
        def __init__(self):
            self.invocations = []

        def invoke(self, prompt: str):
            """Record invocation and return a pre-defined response object."""
            self.invocations.append(prompt)

            class _Result:
                content = "Os resultados apontam para Brasília."

            return _Result()

    return _FakeLLM()


def test_graph_invoke_returns_completed_state(fake_llm):
    """Happy path should complete with a formatted response."""
    with patch("agente_simples.utils.nodes.config.create_llm", return_value=fake_llm):
        from agente_simples.graph import create_app

        app = create_app()
        result = app.invoke(
            GraphState(
                messages=[{"role": "user", "content": "Qual é a capital do Brasil?"}],
                status="pending",
            )
        )

    assert result["status"] == "completed"
    assert "Resposta do agente" in result["resposta"]
    assert fake_llm.invocations, "LLM should be called at least once"


def test_graph_handles_provider_failure():
    """Provider failures must bubble up as controlled error states."""
    def failing_llm_factory():
        raise RuntimeError("provider offline")

    with patch("agente_simples.utils.nodes.config.create_llm", side_effect=failing_llm_factory):
        from agente_simples.graph import create_app

        app = create_app()
        result = app.invoke(
            GraphState(
                messages=[{"role": "user", "content": "Qual é a capital do Brasil?"}],
                status="pending",
            )
        )

    assert result["status"] == "error"
    assert "problema ao acessar" in result["resposta"].lower()
