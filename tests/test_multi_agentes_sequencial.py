import pytest
from dotenv import load_dotenv
from multi_agentes_sequencial.main import app
from langchain_core.messages import HumanMessage
import json
import re

load_dotenv(dotenv_path="multi_agentes_sequencial/.env")

def test_persona_generation_and_formatting():
    config = {"configurable": {"thread_id": "test-persona-generation"}}
    # The input message can be anything, as the first agent generates a random persona
    # We just need to trigger the graph execution
    result = app.invoke({"messages": [HumanMessage(content="Generate a persona")]}, config=config)

    # Extract JSON from markdown code block
    final_output = result["messages"][-1].content
    json_match = re.search(r"```json\n(.*?)```", final_output, re.DOTALL)
    if json_match:
        json_string = json_match.group(1)
    else:
        json_string = final_output # Assume it's raw JSON if no markdown block

    # Assert that the final output is a valid JSON string
    try:
        persona_json = json.loads(json_string)
    except json.JSONDecodeError:
        pytest.fail(f"Output is not valid JSON: {json_string}")

    # Assert that the JSON contains the expected persona attributes
    expected_attributes = ["name", "region", "education", "fears", "likes", "hobbies"]
    for attr in expected_attributes:
        assert attr in persona_json, f"Missing attribute {attr} in generated persona"
