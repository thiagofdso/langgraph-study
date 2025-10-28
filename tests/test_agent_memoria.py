import pytest
from dotenv import load_dotenv
from agente_memoria.main import app
from langchain_core.messages import HumanMessage

load_dotenv(dotenv_path="agente_memoria/.env")

def test_initial_question():
    config = {"configurable": {"thread_id": "test-initial-question"}}
    question = "quanto é 1+1?"
    expected_answer = "2"
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    assert expected_answer in result["messages"][-1].content

def test_recall_previous_question():
    config = {"configurable": {"thread_id": "test-recall-question"}}
    # First interaction
    initial_question = "quanto é 1+1?"
    app.invoke({"messages": [HumanMessage(content=initial_question)]}, config=config)

    # Second interaction, asking about the first question
    follow_up_question = "Qual foi minha primeira pergunta?"
    expected_answer = initial_question
    result = app.invoke({"messages": [HumanMessage(content=follow_up_question)]}, config=config)
    assert expected_answer in result["messages"][-1].content