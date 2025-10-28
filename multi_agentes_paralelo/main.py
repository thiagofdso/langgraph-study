from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Estado compartilhado entre os nós
class State(TypedDict):
    topic: str
    joke: str
    story: str
    poem: str
    combined_output: str

# Nós que executam em paralelo
def call_llm_1(state: State):
    """Gera uma piada"""
    msg = llm.invoke(f"Escreva uma piada sobre {state['topic']}")
    return {"joke": msg.content}

def call_llm_2(state: State):
    """Gera uma história"""
    msg = llm.invoke(f"Escreva uma história sobre {state['topic']}")
    return {"story": msg.content}

def call_llm_3(state: State):
    """Gera um poema"""
    msg = llm.invoke(f"Escreva um poema sobre {state['topic']}")
    return {"poem": msg.content}

def aggregator(state: State):
    """Combina todos os resultados"""
    combined = f"Aqui está uma história, piada e poema sobre {state['topic']}!\n\n"
    combined += f"HISTÓRIA:\n{state['story']}\n\n"
    combined += f"PIADA:\n{state['joke']}\n\n"
    combined += f"POEMA:\n{state['poem']}"
    return {"combined_output": combined}

# Construir o grafo
parallel_builder = StateGraph(State)

# Adicionar os nós
parallel_builder.add_node("call_llm_1", call_llm_1)
parallel_builder.add_node("call_llm_2", call_llm_2)
parallel_builder.add_node("call_llm_3", call_llm_3)
parallel_builder.add_node("aggregator", aggregator)

# Criar conexões paralelas do START para os três nós
parallel_builder.add_edge(START, "call_llm_1")
parallel_builder.add_edge(START, "call_llm_2")
parallel_builder.add_edge(START, "call_llm_3")

# Conectar os três nós ao agregador
parallel_builder.add_edge("call_llm_1", "aggregator")
parallel_builder.add_edge("call_llm_2", "aggregator")
parallel_builder.add_edge("call_llm_3", "aggregator")

# Finalizar
parallel_builder.add_edge("aggregator", END)

# Compilar e executar
parallel_workflow = parallel_builder.compile()
state = parallel_workflow.invoke({"topic": "gatos"})
print(state["combined_output"])
