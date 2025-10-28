import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    thread_id: str

def get_llm():
    # Set up the model
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                 temperature=0,
                                 api_key=os.getenv("GEMINI_API_KEY"))
    return model

def create_graph_builder():
    return StateGraph(AgentState)

def agent_node(state: AgentState, llm_model):
    last_message = state["messages"][-1]
    response = llm_model.invoke([last_message])
    return {"messages": [response]}
