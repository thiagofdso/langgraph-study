import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END

from common import AgentState, get_llm, create_graph_builder, agent_node
from router_agent import route_by_age
from informal_agent import create_informal_agent
from formal_agent import create_formal_agent

load_dotenv()

# Initialize LLM
llm = get_llm()

# Create persona agents
informal_agent_runnable = create_informal_agent()
formal_agent_runnable = create_formal_agent()

# Define agent nodes
def informal_agent_node(state: AgentState):
    question = state["messages"][-1].content.split(":", 1)[1].strip() # Extract question after age
    response = informal_agent_runnable.invoke({"question": question})
    return {"messages": [HumanMessage(content=response)]}

def formal_agent_node(state: AgentState):
    question = state["messages"][-1].content.split(":", 1)[1].strip() # Extract question after age
    response = formal_agent_runnable.invoke({"question": question})
    return {"messages": [HumanMessage(content=response)]}

# Build the graph
builder = create_graph_builder()

builder.add_node("informal_agent", informal_agent_node)
builder.add_node("formal_agent", formal_agent_node)

# Define the entry point and conditional edges for routing
builder.set_entry_point("router")
builder.add_node("router", lambda state: state) # Router node just passes state for routing

builder.add_conditional_edges(
    "router",
    route_by_age,
    {
        "informal_agent": "informal_agent",
        "formal_agent": "formal_agent",
    },
)

builder.add_edge("informal_agent", END)
builder.add_edge("formal_agent", END)

# Compile the graph with memory
memory = InMemorySaver()
app = builder.compile(checkpointer=memory)

async def run_conversation(age: int, question: str, thread_id: str):
    print(f"\n--- Conversation for Thread ID: {thread_id} (Age: {age}) ---")
    user_input = f"{age}: {question}"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initial message to the router
    result = await app.ainvoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    
    # The final message in the state will be the response from the persona agent
    final_response = result["messages"][-1].content
    print(f"User: {user_input}")
    print(f"Agent: {final_response}")

async def main():
    # Simulate conversation for a young user
    await run_conversation(25, "Qual é a capital da França?", "young_user_1")

    # Simulate conversation for a non-young user
    await run_conversation(45, "Poderia me informar a capital da França, por gentileza?", "non_young_user_1")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
