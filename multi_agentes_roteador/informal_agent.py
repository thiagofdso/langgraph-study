from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from common import get_llm

def create_informal_agent():
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente super amigável e descolado! Use MUITOS emojis e gírias bem jovens em suas respostas. Seja bem informal e divertido!"),
        ("human", "{question}")
    ])
    return prompt | llm | StrOutputParser()
