"""Console entry point for a simple Tavily + LangGraph research demo."""

from __future__ import annotations

import os
from textwrap import dedent
from typing import List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph

load_dotenv(dotenv_path="agente_web/.env")

QUESTION = "Como pesquisar arquivos no linux?"
SYSTEM_PROMPT = (
    "Você é um assistente de pesquisa. Resuma as descobertas em português, cite "
    "as fontes pelo nome do site e destaque dicas práticas." \
)
SUMMARY_PROMPT = (
    "Com base nas fontes listadas, crie um resumo de até 150 palavras com pelo "
    "menos duas fontes e três dicas práticas quando possível." \
)

TAVILY_KEY = os.getenv("TAVILY_API_KEY", "").strip()
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not TAVILY_KEY or not GEMINI_KEY:
    raise SystemExit(
        "Defina TAVILY_API_KEY e GEMINI_API_KEY no arquivo .env antes de executar o agente."
    )

os.environ.setdefault("GOOGLE_API_KEY", GEMINI_KEY)
os.environ.setdefault("TAVILY_API_KEY", TAVILY_KEY)

search_tool = TavilySearch(max_results=5, topic="general")
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=GEMINI_KEY)


class AgentState(TypedDict):
    question: str
    results: List[dict]
    summary: str
    warnings: List[str]


def fetch_node(state: AgentState) -> AgentState:
    """Consultar Tavily e armazenar resultados simples."""

    try:
        payload = search_tool.invoke({"query": state["question"]})
        state["results"] = payload.get("results", [])
        if not state["results"]:
            state["warnings"].append("Nenhum resultado retornado pela Tavily.")
        elif len(state["results"]) < 2:
            state["warnings"].append("Poucos resultados encontrados.")
    except Exception as exc:  # pragma: no cover - erro externo
        state["warnings"].append(f"Erro na busca: {exc}")
        state["results"] = []
    return state


def summarize_node(state: AgentState) -> AgentState:
    """Gerar resumo curto usando Gemini."""

    results = state["results"]
    if not results:
        state["summary"] = "Não foi possível gerar um resumo por falta de resultados."
        return state

    bullets = []
    for item in results[:5]:
        title = item.get("title", "Sem título")
        url = item.get("url", "")
        content = item.get("content") or item.get("text") or ""
        bullets.append(f"Fonte: {title}\nURL: {url}\nResumo: {content}")

    message = dedent(
        f"""
        {SUMMARY_PROMPT}

        Pergunta original: {state['question']}

        Fontes coletadas:\n""" + "\n\n".join(bullets)
    ).strip()

    response = model.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=message),
    ])

    content = response.content if isinstance(response.content, str) else "".join(response.content)
    state["summary"] = content.strip()
    return state


workflow = StateGraph(AgentState)
workflow.add_node("buscar", fetch_node)
workflow.add_node("resumir", summarize_node)
workflow.add_edge(START, "buscar")
workflow.add_edge("buscar", "resumir")
workflow.add_edge("resumir", END)
app = workflow.compile()


def main() -> None:
    initial: AgentState = {
        "question": QUESTION,
        "results": [],
        "summary": "",
        "warnings": [],
    }

    final_state = app.invoke(initial)

    print("Pergunta:", QUESTION)
    print("\nResumo:\n", final_state["summary"] or "(vazio)")

    if final_state["warnings"]:
        print("\nAvisos:")
        for note in final_state["warnings"]:
            print(f"- {note}")

    if final_state["results"]:
        print("\nFontes:")
        for item in final_state["results"][:5]:
            print(f"* {item.get('title', 'Sem título')} -> {item.get('url', '')}")

    _write_report(final_state)


def _write_report(state: AgentState) -> None:
    lines = [
        "Pergunta:",
        state["question"],
        "",
        "Resumo:",
        state["summary"] or "(vazio)",
        "",
        "Avisos:",
    ]
    lines.extend(f"- {note}" for note in state["warnings"] or ["(nenhum)"])
    lines.append("")
    lines.append("Fontes:")
    if state["results"]:
        for item in state["results"][:5]:
            lines.append(f"* {item.get('title', 'Sem título')} -> {item.get('url', '')}")
    else:
        lines.append("(nenhuma)")

    with open("agente_web/smoke_test_output.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


if __name__ == "__main__":
    main()
