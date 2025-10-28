import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, List, Any
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage

load_dotenv(dotenv_path="agente_memoria/.env")

# Set up the model
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                             temperature=0,
                             api_key=os.getenv("GEMINI_API_KEY"))

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# Define the agent
def agent_node(state: AgentState):
    messages = state["messages"]
    output = model.invoke(messages)
    messages.append(output)
    return {"messages": messages}

# Define the graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

# Compile the graph with a checkpointer for memory
memory = InMemorySaver()
app = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # Initialize state for a new conversation thread
    config = {"configurable": {"thread_id": "conversation-1"}}

    # First question
    first_question = "quanto é 1+1?"
    print(f"User: {first_question}")
    result = app.invoke({"messages": [HumanMessage(content=first_question)]}, config=config)
    print(f"Agent: {result["messages"][-1].content}")

    # Second question, testing memory
    second_question = "Some esse valor com 10?"
    print(f"User: {second_question}")
    result = app.invoke({"messages": [HumanMessage(content=second_question)]}, config=config)
    print(f"Agent: {result["messages"][-1].content}")
