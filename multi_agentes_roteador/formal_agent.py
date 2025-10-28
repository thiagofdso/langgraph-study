from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from common import get_llm

def create_formal_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente formal e cordial. Responda de forma educada e profissional."),
        ("human", "{question}")
    ])
    return prompt | llm | StrOutputParser()
