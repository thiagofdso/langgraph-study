import pytest
from informal_agent import create_informal_agent
from formal_agent import create_formal_agent
from langchain_core.messages import HumanMessage
from common import AgentState, get_llm

import asyncio
from unittest.mock import patch
from io import StringIO
from dotenv import load_dotenv

load_dotenv()
llm = get_llm()


@pytest.mark.asyncio
async def test_informal_agent():
    informal_agent = create_informal_agent()
    response = informal_agent.invoke({"question": "E aí, tudo beleza?"})
    assert isinstance(response, str)
    assert any(emoji in response for emoji in ["😊", "👍", "😂", "😎"])
    assert "e aí" in response.lower() or "beleza" in response.lower() or "top" in response.lower()

@pytest.mark.asyncio
async def test_formal_agent():
    formal_agent = create_formal_agent()
    response = formal_agent.invoke({"question": "Poderia me informar a hora atual?"})
    assert isinstance(response, str)
    assert "por favor" in response.lower() or "poderia" in response.lower() or "agradeço" in response.lower()
    assert not any(emoji in response for emoji in ["😊", "👍", "😂", "😎"])

@pytest.mark.asyncio
async def test_router_simulation():
    from main import main
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        await main()
        output = mock_stdout.getvalue()
        
        # Assertions for young user conversation
        assert "--- Conversation for Thread ID: young_user_1 (Age: 25) ---" in output
        assert "User: 25: Qual é a capital da França?" in output
        assert "Agent:" in output # Check if agent responded
        assert any(emoji in output for emoji in ["😊", "👍", "😂", "😎"]) # Check for emojis
        assert "e aí" in output.lower() or "beleza" in output.lower() or "top" in output.lower() # Check for informal language
        
        # Assertions for non-young user conversation
        assert "--- Conversation for Thread ID: non_young_user_1 (Age: 45) ---" in output
        assert "User: 45: Poderia me informar a capital da França, por gentileza?" in output
        assert "Agent:" in output # Check if agent responded
        assert "por favor" in output.lower() or "poderia" in output.lower() or "agradeço" in output.lower() # Check for formal language
        assert not any(emoji in output for emoji in ["😊", "👍", "😂", "😎"])
