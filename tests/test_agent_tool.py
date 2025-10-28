import pytest
from dotenv import load_dotenv
from agente_tool.main import app
from langchain_core.messages import HumanMessage

load_dotenv(dotenv_path="agente_tool/.env")

def test_calculator_tool_usage():
    config = {"configurable": {"thread_id": "test-calculator-tool"}}
    question = "quanto é 300 dividido por 4?"
    expected_answer = "75"
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    assert expected_answer in result["messages"][-1].content
