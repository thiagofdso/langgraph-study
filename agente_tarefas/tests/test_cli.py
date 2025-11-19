from copy import deepcopy

from langchain_core.messages import AIMessage, SystemMessage

from agente_tarefas import cli
from agente_tarefas.state import AgentState, state_factory


class DummyApp:
    """Placeholder graph object used solely for CLI tests."""

    def invoke(self, payload, config):  # pragma: no cover - not used directly
        raise AssertionError("DummyApp.invoke should be mocked via _invoke_agent")


def test_cli_runs_three_rounds(monkeypatch):
    inputs = iter([
        "Estudar, Lavar",  # round 1 tasks
        "1",  # round 2 selection
        "Nova tarefa",  # round 3 new tasks
    ])
    outputs: list[str] = []

    def fake_input(prompt: str) -> str:  # noqa: ARG001 - needed for signature
        return next(inputs)

    def fake_print(message: str) -> None:
        outputs.append(message)

    monkeypatch.setattr(cli, "create_graph", lambda _settings: DummyApp())
    monkeypatch.setattr(cli, "preflight_config_check", lambda: [])

    # Prepare fake states returned by the graph for each round
    round1_state: AgentState = state_factory.build(messages=[SystemMessage(content="sys")])
    round1_state.update(
        {
            "tasks": [
                {"id": 1, "description": "Estudar", "status": "pending", "source_round": "round1"},
                {"id": 2, "description": "Lavar", "status": "pending", "source_round": "round1"},
            ],
            "timeline": [
                {
                    "round_id": "round1",
                    "user_input": "Estudar, Lavar",
                    "agent_response": "resposta 1",
                }
            ],
            "messages": [SystemMessage(content="sys"), AIMessage(content="resposta 1")],
            "round_payload": {},
        }
    )

    round2_state: AgentState = deepcopy(round1_state)
    round2_state["messages"].append(AIMessage(content="resposta 2"))
    round2_state["completed_ids"] = [1]
    round2_state["tasks"][0]["status"] = "completed"
    round2_state["timeline"].append(
        {
            "round_id": "round2",
            "user_input": "1",
            "agent_response": "resposta 2",
        }
    )

    round3_state: AgentState = deepcopy(round2_state)
    round3_state["messages"].append(AIMessage(content="resposta 3"))
    round3_state["tasks"].append(
        {"id": 3, "description": "Nova tarefa", "status": "pending", "source_round": "round3"}
    )
    round3_state["timeline"].append(
        {
            "round_id": "round3",
            "user_input": "Nova tarefa",
            "agent_response": "resposta 3",
        }
    )

    responses = iter([round1_state, round2_state, round3_state])

    def fake_invoke_agent(app, *, thread_id, state):  # noqa: ARG001 - signature mimic
        return deepcopy(next(responses))

    monkeypatch.setattr(cli, "_invoke_agent", fake_invoke_agent)

    cli.run_cli(input_fn=fake_input, output_fn=fake_print)

    agent_lines = [line for line in outputs if line.startswith("Agente:")]
    assert len(agent_lines) == 3
    assert agent_lines[-1].endswith("resposta 3")
