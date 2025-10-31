"""Console entry point for the Reflexion Web Evidence Agent."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from textwrap import dedent
from typing import Dict, List, Literal, TypedDict
from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

QUESTION = "Como funciona o Google Agent Development Kit?"
MAX_REFLECTIONS = 3

GENERATION_SYSTEM_PROMPT = (
    "Você é um redator técnico em português responsável por explicar o "
    "Google Agent Development Kit (GADK) com precisão, clareza e foco prático."
)

REFLECTION_SYSTEM_PROMPT = (
    "Você é um revisor criterioso. Avalie o rascunho à luz das evidências e "
    "descreva o que precisa ser ajustado antes da publicação."
)

load_dotenv(dotenv_path="agente_reflexao_web/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

if not GEMINI_API_KEY or not TAVILY_API_KEY:
    raise SystemExit(
        "Defina GEMINI_API_KEY e TAVILY_API_KEY em agente_reflexao_web/.env antes de executar o agente."
    )

os.environ.setdefault("GOOGLE_API_KEY", GEMINI_API_KEY)
os.environ.setdefault("TAVILY_API_KEY", TAVILY_API_KEY)

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=GEMINI_API_KEY)
reflection_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, api_key=GEMINI_API_KEY)
search_tool = TavilySearch(max_results=6, search_depth="advanced")


class IterationRecord(TypedDict):
    draft: str
    reflection: str
    references: Dict[str, str]


class AgentState(TypedDict):
    question: str
    draft: str
    reflections: List[str]
    results: List[dict]
    references: Dict[str, str]
    history: List[IterationRecord]
    iteration: int
    reflection_count: int
    max_reflections: int
    last_reflection: str
    warnings: List[str]
    next_step: Literal["reflect", "gerar", "end"]


def _build_reference_block(results: List[dict]) -> tuple[Dict[str, str], str]:
    if not results:
        return {}, "Nenhuma evidência coletada até o momento."

    mapping: Dict[str, str] = {}
    lines: List[str] = []
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    for idx, item in enumerate(results, start=1):
        ref = f"ref-{idx}"
        url = item.get("url") or ""
        title = item.get("title") or "Sem título"
        snippet = (item.get("content") or item.get("text") or "").replace("\n", " ").strip()
        if len(snippet) > 280:
            snippet = snippet[:277] + "..."
        site = urlparse(url).netloc or "Fonte desconhecida"
        lines.append(f"[{ref}] {title} — {site}\nURL: {url}\nResumo: {snippet}")
        mapping[ref] = url
    return mapping, "\n".join(lines)


def _apply_urls(text: str, references: Dict[str, str]) -> str:
    result = text
    for ref, url in references.items():
        if not url:
            continue
        escaped = re.escape(ref)
        replacements = [
            (rf"\[\s*{escaped}\s*\]", f"({url})"),
            (rf"\(\s*{escaped}\s*\)", f"({url})"),
            (rf"\b{escaped}\b", f"({url})"),
        ]
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


def _collect_citations(raw_text: str, references: Dict[str, str], results: List[dict]) -> List[str]:
    used_refs = [ref for ref in references if re.search(rf"\b{re.escape(ref)}\b", raw_text)]
    if not used_refs:
        used_refs = list(references.keys())[:2]

    citations: List[str] = []
    for ref in used_refs:
        url = references.get(ref, "")
        if not url:
            continue
        try:
            idx = int(ref.split("-")[-1]) - 1
            title = results[idx].get("title", "Sem título")
        except (ValueError, IndexError):
            title = "Sem título"
        citations.append(f"{title} — {url}")
    return citations


def gerar_resposta(state: AgentState) -> Dict[str, object]:
    iteration = state["iteration"] + 1
    ref_block_mapping, ref_block_text = _build_reference_block(state["results"])
    # Mantenha mapeamento atual até nova reflexão fornecer fontes mais recentes
    references = state["references"] or ref_block_mapping

    guidance = state["last_reflection"] or "Nenhuma reflexão anterior registrada."
    prompt = dedent(
        f"""
        Pergunta: {state['question']}

        Orientações mais recentes:
        {guidance}

        Evidências disponíveis (use identificadores [ref-n] ao citar):
        {ref_block_text}

        Instruções:
        - Explique como o Google Agent Development Kit funciona, cobrindo criação de agentes Gemini, conectores com Google Workspace, governança no Agentspace, integrações com Application Integration e implantação no Agent Engine.
        - Use linguagem clara em português, com bullets quando apropriado.
        - Atribua cada afirmação factual a uma evidência [ref-n] do bloco acima.
        - Finalize com um parágrafo de próximos passos recomendados.
        """
    ).strip()

    response = model.invoke(
        [
            SystemMessage(content=GENERATION_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ]
    )

    draft = response.content.strip() if isinstance(response.content, str) else "".join(response.content)
    history = state["history"] + [
        {
            "draft": draft,
            "reflection": "",
            "references": references,
        }
    ]

    return {
        "draft": draft,
        "iteration": iteration,
        "history": history,
        "next_step": "reflect",
    }


def decidir_fluxo(state: AgentState) -> Dict[str, object]:
    reached_limit = state["reflection_count"] >= state["max_reflections"]
    if reached_limit:
        next_step: Literal["reflect", "gerar", "end"] = "end"
        reason = "Limite máximo de reflexões alcançado; encerrando com a última versão."
    else:
        next_step = "reflect"
        reason = "Executar nova reflexão para fortalecer a resposta."

    return {
        "next_step": next_step,
        "decision_reason": reason,
        "warnings": state["warnings"],
    }


def refletir_com_evidencias(state: AgentState) -> Dict[str, object]:
    query = f"{state['question']} {state['draft'][:120]}"
    warnings = state["warnings"][:]

    try:
        payload = search_tool.invoke({"query": query})
        results = payload.get("results", []) if isinstance(payload, dict) else []
    except Exception as exc:  # pragma: no cover - acesso externo
        results = []
        warnings.append(f"Falha ao consultar Tavily: {exc}")

    if not results:
        warnings.append("Nenhuma evidência nova encontrada; reutilizando fontes anteriores se disponíveis.")
        results = state["results"] or []

    references, ref_block_text = _build_reference_block(results)

    reflection_prompt = dedent(
        f"""
        Pergunta original: {state['question']}

        Rascunho atual a ser revisado:
        {state['draft']}

        Evidências recuperadas (identificadores [ref-n]):
        {ref_block_text}

        Responda em JSON com os campos:
        {{
            "comentario_geral": "...",
            "mudancas_obrigatorias": ["..."],
            "pronto_para_publicar": true/false
        }}
        """
    ).strip()

    response = reflection_model.invoke(
        [
            SystemMessage(content=REFLECTION_SYSTEM_PROMPT),
            HumanMessage(content=reflection_prompt),
        ]
    )

    raw_reflection = response.content if isinstance(response.content, str) else "".join(response.content)

    try:
        block = _extract_json(raw_reflection)
        payload = json.loads(block)
    except (json.JSONDecodeError, ValueError, TypeError):
        payload = {
            "comentario_geral": raw_reflection.strip(),
            "mudancas_obrigatorias": [],
            "pronto_para_publicar": False,
        }

    comentario = payload.get("comentario_geral") or "Nenhum comentário fornecido."
    melhorias = payload.get("mudancas_obrigatorias") or []

    reflection_lines = [f"Comentário geral: {comentario}"]
    if melhorias:
        reflection_lines.append("Mudanças obrigatórias:")
        reflection_lines.extend(f"- {item}" for item in melhorias)

    reflection_text = "\n".join(reflection_lines)

    history = state["history"][:]
    if history:
        history[-1] = {
            "draft": history[-1]["draft"],
            "reflection": reflection_text,
            "references": references,
        }

    reflections = state["reflections"] + [reflection_text]

    return {
        "reflections": reflections,
        "results": results,
        "references": references,
        "history": history,
        "last_reflection": reflection_text,
        "reflection_count": state["reflection_count"] + 1,
        "warnings": warnings,
        "next_step": "gerar",
    }


def _extract_json(raw: str) -> str:
    candidate = raw.strip()
    if candidate.startswith("```"):
        segments = candidate.split("```")
        if len(segments) >= 3:
            candidate = segments[1]
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("JSON não encontrado")
    return candidate[start : end + 1]


def _finalize_answer(state: AgentState) -> Dict[str, object]:
    raw_draft = state["draft"]
    references = state["references"]
    formatted = _apply_urls(raw_draft, references)
    citations = _collect_citations(raw_draft, references, state["results"])
    return {"answer": formatted, "citations": citations}


def _print_history(state: AgentState) -> None:
    print("\n=== Histórico de Iterações ===")
    if not state["history"]:
        print("(Nenhuma iteração registrada)")
        return

    for idx, item in enumerate(state["history"], start=1):
        refs = item["references"]
        print(f"\nIteração {idx}")
        print("Rascunho:")
        print(_apply_urls(item["draft"], refs))
        if item["reflection"]:
            print("\nReflexão:")
            print(_apply_urls(item["reflection"], refs))
        else:
            print("\nReflexão: (pendente)")


def _print_citations(citations: List[str]) -> None:
    print("\n=== Referências ===")
    if not citations:
        print("(Nenhuma referência identificada)")
        return
    for citation in citations:
        print(citation)


memory = InMemorySaver()

graph = StateGraph(AgentState)
graph.add_node("gerar_resposta", gerar_resposta)
graph.add_node("decidir_fluxo", decidir_fluxo)
graph.add_node("refletir_com_evidencias", refletir_com_evidencias)
graph.add_edge(START, "gerar_resposta")
graph.add_edge("gerar_resposta", "decidir_fluxo")
graph.add_conditional_edges(
    "decidir_fluxo",
    lambda state: state["next_step"],
    {"reflect": "refletir_com_evidencias", "end": END},
)
graph.add_edge("refletir_com_evidencias","gerar_resposta")
app = graph.compile(checkpointer=memory)


def main() -> None:
    initial_state: AgentState = {
        "question": QUESTION,
        "draft": "",
        "reflections": [],
        "results": [],
        "references": {},
        "history": [],
        "iteration": 0,
        "reflection_count": 0,
        "max_reflections": MAX_REFLECTIONS,
        "last_reflection": "",
        "warnings": [],
        "next_step": "reflect",
    }

    config = {"configurable": {"thread_id": "reflexao-web"}}
    final_state = app.invoke(initial_state, config=config)
    output = _finalize_answer(final_state)

    print("Pergunta:", QUESTION)
    print("\n=== Resposta Final ===")
    print(output["answer"] or "(Sem resposta gerada)")
    _print_citations(output["citations"])
    _print_history(final_state)

    if final_state["warnings"]:
        print("\n=== Avisos ===")
        for warning in final_state["warnings"]:
            print(f"- {warning}")

    print("\nDecisão final:", final_state.get("decision_reason", ""))


if __name__ == "__main__":
    main()
