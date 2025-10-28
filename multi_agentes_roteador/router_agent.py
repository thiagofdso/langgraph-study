from typing import Literal
from common import AgentState, get_llm
from langchain_core.messages import HumanMessage

def route_by_age(state: AgentState) -> Literal["informal_agent", "formal_agent"]:
    # Assuming the age is passed in the first message content, e.g., "25: Qual é a capital da França?"
    first_message_content = state["messages"][0].content
    try:
        age_str = first_message_content.split(":")[0].strip()
        age = int(age_str)
    except (ValueError, IndexError):
        # Default to formal if age is not provided or invalid
        return "formal_agent"

    if age <= 30:
        return "informal_agent"
    else:
        return "formal_agent"

def router_agent_node(state: AgentState):
    # The router agent itself doesn't generate a response, it just routes.
    # This node is primarily for defining the routing logic within the graph.
    return state
