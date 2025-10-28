import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, List, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage
from langchain.tools import tool
from langgraph.prebuilt import ToolNode

load_dotenv(dotenv_path="agente_tool/.env")

# Set up the model
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                             temperature=0,
                             api_key=os.getenv("GEMINI_API_KEY"))

# Define the calculator tool
@tool
def calculator(expression: str) -> str:
    """Use this tool to evaluate mathematical expressions. Input should be a string representing a mathematical expression (e.g., '2+2', '300/4')."""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

# Define the agent node
def agent_node(state: AgentState):
    current_message = state["messages"][-1]
    response = model.invoke([current_message])
    return {"messages": [response]}

# Define the graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("calculator_tool", ToolNode([calculator]))

workflow.set_entry_point("agent")

def route_agent(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "calculator_tool"
    return END

workflow.add_conditional_edges(
    "agent",
    route_agent,
)
workflow.add_edge("calculator_tool", END)

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "calculator-conversation"}}
    question = "quanto é 300 dividido por 4?"
    print(f"User: {question}")
    result = app.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    print(f"Agent: {result["messages"][-1].content}")
