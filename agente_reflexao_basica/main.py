import os
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv(dotenv_path="agente_reflexao_basica/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise SystemExit(
        "Defina GEMINI_API_KEY em agente_reflexao_basica/.env antes de executar o agente."
    )

MODEL = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    api_key=GEMINI_API_KEY,
)
QUESTION = "O que é importante para um programador aprender"
# Ajuste este valor para controlar quantas mensagens (pergunta + rascunhos + reflexões) são permitidas.
# Equivale, aproximadamente, a pergunta inicial + (limite // 2) ciclos draft/reflexão.
MESSAGE_LIMIT = 6


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


def generate(state: AgentState) -> dict:
    prompt_lines = [
        "Você é um mentor de carreira para programadores iniciantes.",
        f"Pergunta fixa: {QUESTION}.",
        "Produza texto em português com pelo menos quatro prioridades distintas (ex.: fundamentos de lógica, versionamento, testes, habilidades colaborativas).",
        "Organize a resposta em parágrafos curtos e claros.",
    ]
    previous_reflections = [
        msg.content for msg in state["messages"] if getattr(msg, "name", "") == "reflection"
    ]
    if previous_reflections:
        prompt_lines.append("Incorpore completamente estas recomendações:")
        prompt_lines.extend(previous_reflections[-1:])
    response = MODEL.invoke("\n".join(prompt_lines))
    return {"messages": [AIMessage(content=response.content, name="draft")]}


def reflect(state: AgentState) -> dict:
    drafts = [msg for msg in state["messages"] if getattr(msg, "name", "") == "draft"]
    draft_text = drafts[-1].content if drafts else ""
    prompt = (
        "Você é um revisor criterioso. Liste pontos fortes e depois melhorias necessárias."
        " Use bullet points curtos."
        f"\nRascunho analisado:\n{draft_text}"
    )
    response = MODEL.invoke(prompt)
    return {"messages": [AIMessage(content=response.content, name="reflection")]} 


def should_continue(state: AgentState) -> str:
    if len(state["messages"]) > MESSAGE_LIMIT:
        return END
    return "reflect"


def build_app():
    graph = StateGraph(AgentState)
    graph.add_node("generate", generate)
    graph.add_node("reflect", reflect)
    graph.add_edge(START, "generate")
    graph.add_conditional_edges(
        "generate",
        should_continue,
        {"reflect": "reflect", END: END},
    )
    graph.add_edge("reflect", "generate")
    return graph.compile()


def run_once():
    app = build_app()
    result = app.invoke(
        {"messages": [HumanMessage(content=QUESTION, name="pergunta")]},
    )
    final_messages = result["messages"]
    drafts = [msg for msg in final_messages if getattr(msg, "name", "") == "draft"]
    reflections = [msg for msg in final_messages if getattr(msg, "name", "") == "reflection"]

    print("=== Reflexões ===")
    if reflections:
        for idx, message in enumerate(reflections, start=1):
            print(f"Reflexão {idx}:")
            print(message.content.strip(), "\n")
    else:
        print("Nenhuma reflexão registrada.\n")

    print("=== Rascunhos ===")
    if drafts:
        for idx, message in enumerate(drafts, start=1):
            print(f"Draft {idx}:")
            print(message.content.strip(), "\n")
        final_answer = drafts[-1].content.strip()
    else:
        print("Nenhum rascunho gerado.\n")
        final_answer = ""

    print("=== Resposta Final ===")
    print(final_answer)


if __name__ == "__main__":
    run_once()
