import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Dict

load_dotenv()

# Set up the model
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                             temperature=0,
                             api_key=os.getenv("GEMINI_API_KEY"))

class GraphState(TypedDict):
    question: str
    answer: str

# Define the agent
def agent(state: GraphState) -> Dict[str, str]:
    question = state["question"]
    generation = model.invoke(question)
    return {"answer": generation.content}

# Define the graph
workflow = StateGraph(GraphState)
workflow.add_node("agent", agent)
workflow.set_entry_point("agent")
workflow.set_finish_point("agent")

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    question = input("Ask a question: ")
    result = app.invoke({"question": question})
    print(result["answer"])