from langchain_core.messages import AIMessage

from agente_tarefas import cli


class DummyApp:
    def __init__(self):
        self.counter = 0

    def invoke(self, payload, config):
        self.counter += 1
        return {
            "messages": payload["messages"] + [AIMessage(content=f"resposta {self.counter}")]
        }


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

    cli.run_cli(input_fn=fake_input, output_fn=fake_print)

    agent_lines = [line for line in outputs if line.startswith("Agente:")]
    assert len(agent_lines) == 3
    assert agent_lines[-1].endswith("resposta 3")
