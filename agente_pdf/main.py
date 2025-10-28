import os
import logging
from typing import TypedDict, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Define Graph State
class AgentState(TypedDict):
    pdf_path: str
    pdf_content: List[Document]
    user_query: str
    llm_response: str
    markdown_output: str

# Nodes
def load_and_parse_pdf(state: AgentState) -> AgentState:
    pdf_path = state['pdf_path']
    logging.info(f"Loading and parsing PDF: {pdf_path}")
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        return {**state, "pdf_content": docs}
    except Exception as e:
        logging.error(f"Error loading or parsing PDF {pdf_path}: {e}")
        return {**state, "pdf_content": []} # Indicate failure

def invoke_llm(state: AgentState) -> AgentState:
    pdf_content = state['pdf_content']
    user_query = state['user_query']
    if not pdf_content:
        return {**state, "llm_response": None} # Skip if PDF loading failed

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.1)

    logging.info("Invoking LLM with PDF content and query.")
    try:
        context = " ".join([doc.page_content for doc in pdf_content])
        message = HumanMessage(
            content=f"Baseando-se no PDF: {context}\nResponda: {user_query}"
        )
        response = llm.invoke([message])
        return {**state, "llm_response": response.content}
    except Exception as e:
        logging.error(f"Error during LLM interaction: {e}")
        return {**state, "llm_response": None}

def parse_llm_response(state: AgentState) -> AgentState:
    llm_response = state['llm_response']
    if not llm_response:
        return {**state, "markdown_output": None} # Skip if LLM invocation failed

    logging.info("LLM response parsed and markdown generated.")
    return {**state, "markdown_output": llm_response}

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("load_and_parse_pdf", load_and_parse_pdf)
workflow.add_node("invoke_llm", invoke_llm)
workflow.add_node("parse_response", parse_llm_response)

workflow.set_entry_point("load_and_parse_pdf")

workflow.add_edge("load_and_parse_pdf", "invoke_llm")
workflow.add_edge("invoke_llm", "parse_response")
workflow.add_edge("parse_response", END)

app = workflow.compile()

if __name__ == "__main__":
    # Hardcoded values as per user request
    pdf_file = "openshift_container_platform-4.9-distributed_tracing-en-us.pdf"
    user_query = "como implantar o operator do jaeger usando web console do openshift"

    initial_state = {
        "pdf_path": pdf_file,
        "pdf_content": [],
        "user_query": user_query,
        "llm_response": None,
        "markdown_output": None
    }

    logging.info(f"Starting PDF analysis for {pdf_file} with query: {user_query}")
    final_state = app.invoke(initial_state)

    if final_state['markdown_output']:
        print("\n--- Generated Markdown ---")
        print(final_state['markdown_output'])
        print("--------------------------")
    else:
        print("\nFailed to generate markdown from the PDF.")
