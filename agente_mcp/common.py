import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(dotenv_path="agente_mcp/.env")

def get_llm():
    # Set up the model
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
                                 temperature=0,
                                 api_key=os.getenv("GEMINI_API_KEY"))
    return model
