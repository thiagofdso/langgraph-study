"""CLI entrypoint that runs the agente_mcp workflow end-to-end."""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from typing import Iterable, Sequence

if __package__ in {None, ""}:  # pragma: no cover - script execution fallback
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agente_mcp.config import AppConfig, ConfigError, load_app_config
from agente_mcp.graph import create_graph
from agente_mcp.state import AgentSession, bootstrap_session
from agente_mcp.utils.logging import setup_logging
from agente_mcp.utils.servers import (
    ServerProfile,
    build_connection_map,
    load_server_profiles,
)

SYSTEM_PROMPT = (
    "Você é um agente multi-servidor. Utilize as ferramentas MCP disponíveis para responder "
    "perguntas sobre matemática e clima em português claro."
)


def _build_client(profiles: Sequence[ServerProfile]) -> MultiServerMCPClient:
    return MultiServerMCPClient(build_connection_map(profiles))


def _print_manual_server_warnings(
    profiles: Sequence[ServerProfile],
    *,
    logger,
) -> None:
    for profile in profiles:
        if not profile.auto_start:
            logger.warning(
                "Servidor MCP requer inicialização manual",
                server=profile.name,
                endpoint=profile.endpoint,
                transport=profile.transport,
            )


async def _load_tools(
    client: MultiServerMCPClient,
    logger,
) -> Sequence[BaseTool]:
    try:
        tools = await client.get_tools()
    except Exception as exc:  # pragma: no cover - external dependency
        logger.error("Falha ao carregar ferramentas MCP", error=str(exc))
        raise

    if not tools:
        logger.error("Cliente MCP não retornou ferramentas.")
        return []

    if len({tool.name for tool in tools}) != len(tools):
        logger.warning(
            "Foram detectadas ferramentas com nomes duplicados; a última definição prevalecerá."
        )
    return tools


def _pretty_print_response(question: str, state: AgentSession) -> None:
    print(f"User: {question}")
    messages: Sequence[BaseMessage] = state.get("messages", [])
    ai_messages = [msg for msg in messages if isinstance(msg, AIMessage)]
    if ai_messages:
        final_message = ai_messages[-1].content
        print(f"Assistant: {final_message}")
    else:
        print("Assistant: [sem resposta]")
    run_log = state.get("run_log", [])
    if run_log:
        print("Run log:")
        for entry in run_log:
            tool = entry.get("tool_name", "n/a")
            status = entry.get("status")
            duration = entry.get("duration_ms")
            phase = entry.get("phase")
            print(f"  - {phase}: {tool} [{status}] ({duration} ms)")
    print("-" * 30)


async def _run_cli_session(app_config: AppConfig, *, base_thread_id: str) -> None:
    logger = setup_logging()
    profiles = load_server_profiles()
    _print_manual_server_warnings(profiles, logger=logger)
    client = _build_client(profiles)
    tools = await _load_tools(client, logger)
    if not tools:
        logger.error("Nenhuma ferramenta MCP foi carregada")
        return
    tool_lookup = {tool.name: tool for tool in tools}
    llm_with_tools = app_config.create_llm().bind_tools(tools)
    graph = create_graph(
        {
            "configurable": {
                "app_config": app_config,
                "logger": logger,
                "llm_with_tools": llm_with_tools,
                "tool_lookup": tool_lookup,
            }
        }
    )

    questions = app_config.default_questions
    if not questions:
        logger.error("Nenhuma pergunta padrão definida em MCP_DEFAULT_QUESTIONS")
        return

    for index, question in enumerate(questions, start=1):
        thread_id = base_thread_id or f"{app_config.thread_id}-{index}"
        session = bootstrap_session(
            thread_id=thread_id,
            system_prompt=SYSTEM_PROMPT,
            user_messages=[question],
            metadata={"servers": [profile.name for profile in profiles]},
        )
        state = await graph.ainvoke(
            session,
            config={"configurable": {"thread_id": thread_id}},
        )
        _pretty_print_response(question, state)


def main(argv: Sequence[str] | None = None) -> int:
    argv = tuple(argv or [])
    try:
        app_config = load_app_config()
    except ConfigError as exc:
        print(f"[config] {exc}")
        return 1

    try:
        user_thread_id = argv[0] if argv else ""
        asyncio.run(_run_cli_session(app_config, base_thread_id=user_thread_id))
    except KeyboardInterrupt:  # pragma: no cover - user interrupt
        return 130
    except Exception as exc:  # pragma: no cover - surface unexpected errors
        print(f"[error] {exc}")
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - script execution
    raise SystemExit(main(sys.argv[1:]))
