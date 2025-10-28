import logging
import os
from PIL import Image
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

from agente_imagem.utils import image_to_base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Define Graph State
class AgentState(TypedDict):
    image_path: str
    base64_image: str
    llm_response: str
    markdown_output: str

# Nodes
def validate_and_encode_image(state: AgentState) -> AgentState:
    image_path = state['image_path']
    if not os.path.exists(image_path):
        logging.error(f"Image file not found: {image_path}")
        return {**state, "base64_image": None} # Indicate failure

    try:
        img = Image.open(image_path)
        img.verify()  # Verify that it is an image
    except Exception as e:
        logging.error(f"Error opening or verifying image {image_path}: {e}")
        return {**state, "base64_image": None} # Indicate failure

    logging.info(f"Image validated and encoding: {image_path}")
    base64_image = image_to_base64(image_path)
    return {**state, "base64_image": base64_image}

def invoke_llm(state: AgentState) -> AgentState:
    base64_image = state['base64_image']
    if not base64_image:
        return {**state, "llm_response": None} # Skip if image validation failed

    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)

    logging.info("Invoking LLM with image.")
    try:
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Analyze this mind map image and extract its hierarchical structure. Represent the structure as a markdown string, using headings and lists to show hierarchy. Only include node text and hierarchical level. If the image is not a mind map or is unclear, respond with 'INVALID_IMAGE'.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
            ]
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

    if "INVALID_IMAGE" in llm_response:
        logging.warning("LLM determined image is invalid.")
        return {**state, "markdown_output": None}

    logging.info("LLM response parsed and markdown generated.")
    return {**state, "markdown_output": llm_response}

# Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("validate_and_encode", validate_and_encode_image)
workflow.add_node("invoke_llm", invoke_llm)
workflow.add_node("parse_response", parse_llm_response)

workflow.set_entry_point("validate_and_encode")

workflow.add_edge("validate_and_encode", "invoke_llm")
workflow.add_edge("invoke_llm", "parse_response")
workflow.add_edge("parse_response", END)

app = workflow.compile()

if __name__ == "__main__":
    image_file = "folder_map.png"

    # Create a dummy folder_map.png for testing purposes if it doesn't exist
    if not os.path.exists(image_file):
        try:
            img = Image.new('RGB', (60, 30), color = 'red')
            img.save(image_file)
            logging.info(f"Created a dummy {image_file} for testing.")
        except Exception as e:
            logging.error(f"Could not create dummy {image_file}: {e}")

    initial_state = {"image_path": image_file, "base64_image": None, "llm_response": None, "markdown_output": None}
    final_state = app.invoke(initial_state)

    if final_state['markdown_output']:
        print("\n--- Generated Markdown ---")
        print(final_state['markdown_output'])
        print("--------------------------")
    else:
        print("\nFailed to generate markdown from the image.")
