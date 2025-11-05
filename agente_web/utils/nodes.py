"""Graph node implementations for the agente_web workflow."""

from __future__ import annotations

from textwrap import dedent
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.prebuilt import ToolNode

from agente_web.prompts import SUMMARY_PROMPT, SYSTEM_PROMPT
from agente_web.state import GraphState
from agente_web.utils.tools import (
    build_search_tool_calls,
    merge_warnings,
    parse_tool_payload,
)


def _clean_content(message: BaseMessage | Dict[str, Any]) -> str:
    """Extract textual content from LangChain or dict-styled messages."""

    if isinstance(message, BaseMessage):
        content = getattr(message, "content", "")
    elif isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = ""

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
        content = "".join(parts)

    return str(content or "").strip()


def _extract_question(state: GraphState) -> str:
    """Return the latest human question from the messages buffer."""

    messages = state.get("messages") or []
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            text = _clean_content(message)
            if text:
                return text
        if isinstance(message, dict):
            role = str(message.get("role") or "").lower()
            if role in {"human", "user"}:
                text = _clean_content(message)
                if text:
                    return text
    existing = state.get("question")
    if isinstance(existing, str):
        return existing.strip()
    return ""


def buscar(
    state: GraphState,
    *,
    tool_runner: ToolNode,
    tool_name: str,
    max_results: int,
) -> Dict[str, Any]:
    """Execute the Tavily search tool via ToolNode and capture normalized results."""

    question = _extract_question(state)
    warnings = merge_warnings(state.get("warnings"))

    if not question:
        return {
            "warnings": merge_warnings(
                warnings,
                "Pergunta ausente. Informe uma pergunta para prosseguir.",
            ),
            "search_results": [],
            "question": "",
        }

    tool_calls = build_search_tool_calls(question, tool_name, max_results=max_results)

    try:
        tool_response = tool_runner.invoke(tool_calls)
    except Exception as exc:  # pragma: no cover - dependência externa
        return {
            "warnings": merge_warnings(
                warnings,
                f"Erro na busca: {exc}",
            ),
            "search_results": [],
            "question": question,
        }

    messages = tool_response.get("messages") or []
    if not messages:
        return {
            "warnings": merge_warnings(
                warnings,
                "Nenhum resultado retornado pela Tavily.",
            ),
            "search_results": [],
            "question": question,
        }

    tool_message = messages[-1]
    results = parse_tool_payload(tool_message.content)
    if not results:
        return {
            "warnings": merge_warnings(
                warnings,
                "Nenhum resultado retornado pela Tavily.",
            ),
            "search_results": [],
            "question": question,
        }

    if len(results) < 2:
        warnings = merge_warnings(warnings, "Poucos resultados encontrados.")

    final_results = results[:max_results]

    metadata = dict(state.get("metadata") or {})
    metadata.update(
        {
            "tool_name": tool_name,
            "tool_call_id": getattr(tool_message, "tool_call_id", None),
            "result_count": len(final_results),
        }
    )

    return {
        "metadata": metadata,
        "messages": messages,
        "search_results": final_results,
        "warnings": warnings,
        "question": question,
    }


def resumir(
    state: GraphState,
    *,
    model: ChatGoogleGenerativeAI,
    system_prompt: str = SYSTEM_PROMPT,
    summary_prompt: str = SUMMARY_PROMPT,
    max_sources: int = 5,
) -> Dict[str, Any]:
    """Generate the final summary using Gemini based on collected results."""

    results = state.get("search_results") or []
    warnings = merge_warnings(state.get("warnings"))

    if not results:
        return {
            "summary": "Não foi possível gerar um resumo por falta de resultados.",
            "warnings": warnings,
        }

    snippets = []
    for item in results[:max_sources]:
        title = item.get("title", "Sem título")
        url = item.get("url", "")
        content = item.get("content", "")
        snippets.append(f"Fonte: {title}\nURL: {url}\nResumo: {content}")

    prompt = dedent(
        f"""
        {summary_prompt}

        Pergunta original: {state.get("question", "")}

        Fontes:\n{'\n\n'.join(snippets)}
        """
    ).strip()

    try:
        response = model.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt),
            ]
        )
    except Exception as exc:  # pragma: no cover - dependência externa
        return {
            "summary": (
                "Não foi possível gerar um resumo devido a um erro na chamada ao modelo."
            ),
            "warnings": merge_warnings(warnings, f"Erro ao gerar resumo: {exc}"),
        }

    content = response.content
    if isinstance(content, list):
        parts = [
            part if isinstance(part, str) else str(part.get("text", ""))
            for part in content
        ]
        content = "".join(parts)

    summary_text = str(content).strip()

    return {
        "summary": summary_text,
        "warnings": warnings,
        "messages": [AIMessage(content=summary_text)],
    }
