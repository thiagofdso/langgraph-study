import pytest
from dotenv import load_dotenv
from agente_simples.main import app

load_dotenv(dotenv_path="agente_simples/.env")

def test_agent():
    question = "quantos estados tem o brasil?"
    expected_answer = "26"
    result = app.invoke({"question": question})
    assert expected_answer in result["answer"]
