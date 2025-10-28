import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage
import json

load_dotenv(dotenv_path="multi_agentes_sequencial/.env")

# Set up the model
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                             temperature=0,
                             api_key=os.getenv("GEMINI_API_KEY"))

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    persona_data: str

# Agent 1: Persona Generator
def generate_persona(state: AgentState):
    prompt = (
        "Generate a random persona with the following attributes: "
        "name, region, education, fears, likes, hobbies. "
        "Present the information in a natural language paragraph."
    )
    response = model.invoke(prompt)
    return {"persona_data": response.content}

# Agent 2: JSON Formatter
def format_persona_to_json(state: AgentState):
    persona_text = state["persona_data"]
    prompt = (
        f"Convert the following persona description into a JSON object. "
        f"Ensure the JSON has keys for name, region, education, fears, likes, and hobbies. "
        f"Persona: {persona_text}"
    )
    response = model.invoke(prompt)
    return {"messages": [HumanMessage(content=response.content)]}

# Define the graph
workflow = StateGraph(AgentState)

workflow.add_node("generator", generate_persona)
workflow.add_node("formatter", format_persona_to_json)

workflow.set_entry_point("generator")
workflow.add_edge("generator", "formatter")
workflow.add_edge("formatter", END)

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "persona-generation-flow"}}
    # Initial input to trigger the graph. The content doesn't matter much here.
    result = app.invoke({"messages": [HumanMessage(content="Start persona generation")]}, config=config)
    print(result["messages"][-1].content)
