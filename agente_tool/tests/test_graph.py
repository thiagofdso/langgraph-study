"""Integration tests for the agente_tool graph."""

from __future__ import annotations

from langchain_core.messages import AIMessage, ToolMessage


class ToolAwareLLM:
    """LLM stub that issues a tool call and then formats the final answer."""

    def __init__(self) -> None:
        self._call_counter = 0

    def invoke(self, messages):  # type: ignore[override]
        self._call_counter += 1
        if self._call_counter == 1:
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "calculator",
                        "args": {"expression": "300 / 4"},
                        "id": "call_1",
                    }
                ],
            )

        tool_messages = [
            message for message in messages if isinstance(message, ToolMessage)
        ]
        if not tool_messages:
            return AIMessage(content="Não foram usadas ferramentas.")

        result = tool_messages[-1].content
        return AIMessage(content=f"Para calcular 300 dividido por 4, obtemos {result}.")


def test_graph_flow_uses_calculator(create_app, initial_state, thread_config):
    app = create_app(llm=ToolAwareLLM())
    config = {"configurable": {"thread_id": thread_config.thread_id}}

    result = app.invoke(initial_state, config=config)

    assert result["status"] == "completed"
    assert result["tool_call"]["name"] == "calculator"
    assert result["tool_call"]["result"] == "75"
    assert "Resposta do agente:" in result["resposta"]
