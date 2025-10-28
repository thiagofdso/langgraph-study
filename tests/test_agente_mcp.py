import pytest
from dotenv import load_dotenv
from agente_mcp.main import app
from langchain_core.messages import HumanMessage
import datetime

load_dotenv(dotenv_path="agente_mcp/.env")

def test_calculator_mcp_service_usage():
    config = {"configurable": {"thread_id": "test-calculator-mcp"}}
    question = "quanto é 150 vezes 3?"
    expected_answer = "450"
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    assert expected_answer in result["messages"][-1].content

def test_time_checking_mcp_service_usage():
    config = {"configurable": {"thread_id": "test-time-checker-mcp"}}
    question = "que horas são agora?"
    # The expected answer should be close to the current time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    assert current_time in result["messages"][-1].content