"""LangGraph builder for agente_mcp."""
from __future__ import annotations

import asyncio
import threading
from functools import partial
from typing import Any, Dict, List

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import END, START, StateGraph
from langgraph.types import RunnableConfig

from agente_mcp.config import AppConfig, load_app_config
from agente_mcp.state import AgentSession
from agente_mcp.utils.logging import setup_logging
from agente_mcp.utils.nodes import (
    execute_tools,
    format_response,
    handle_error,
    invoke_llm,
    validate_input,
)
from agente_mcp.utils.servers import build_connection_map, load_server_profiles


def _fetch_tools_blocking(client: MultiServerMCPClient) -> List[BaseTool]:
    async def _fetch() -> List[BaseTool]:
        return await client.get_tools()

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_fetch())

    result: dict[str, Any] = {}
    error: dict[str, BaseException] = {}

    def _runner() -> None:
        try:
            result["tools"] = asyncio.run(_fetch())
        except BaseException as exc:  # pragma: no cover - thread guard
            error["exc"] = exc

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()
    if error:
        raise error["exc"]
    return result.get("tools", [])


def create_graph(graph_config: RunnableConfig | None) -> Any:
    """Return a compiled StateGraph wired with the MCP nodes."""

    config_section: Dict[str, Any] = {}
    if graph_config and isinstance(graph_config, dict):
        config_section = graph_config.get("configurable", {})

    app_config: AppConfig = config_section.get("app_config") or load_app_config(use_dotenv=False)
    logger = config_section.get("logger") or setup_logging()
    llm_with_tools = config_section.get("llm_with_tools")
    tool_lookup = config_section.get("tool_lookup")
    if llm_with_tools is None or tool_lookup is None:
        profiles = load_server_profiles()
        client = MultiServerMCPClient(build_connection_map(profiles))
        tools = _fetch_tools_blocking(client)
        if not tools:
            raise RuntimeError("Nenhuma ferramenta MCP foi carregada no create_graph.")
        tool_lookup = {tool.name: tool for tool in tools}
        llm_with_tools = app_config.create_llm().bind_tools(tools)

    checkpointer = app_config.create_checkpointer()

    builder = StateGraph(AgentSession)
    builder.add_node(
        "validate_input",
        partial(validate_input, app_config=app_config, logger=logger),
    )
    builder.add_node(
        "invoke_llm",
        partial(invoke_llm, llm_with_tools=llm_with_tools, logger=logger),
    )
    builder.add_node("execute_tools", partial(execute_tools, tools=tool_lookup, logger=logger))
    builder.add_node("format_response", partial(format_response, logger=logger))
    builder.add_node("handle_error", partial(handle_error, logger=logger))

    def _route_after_validation(state: AgentSession) -> str:
        return "handle_error" if state.get("status") == "error" else "invoke_llm"

    def _route_after_invoke(state: AgentSession) -> str:
        if state.get("status") == "error":
            return "handle_error"
        messages = state.get("messages") or []
        if not messages:
            return "handle_error"
        last = messages[-1]
        tool_calls = getattr(last, "tool_calls", None) or []
        return "execute_tools" if tool_calls else "format_response"

    builder.add_edge(START, "validate_input")
    builder.add_conditional_edges("validate_input", _route_after_validation)
    builder.add_conditional_edges("invoke_llm", _route_after_invoke)
    builder.add_edge("execute_tools", "invoke_llm")
    builder.add_edge("handle_error", "format_response")
    builder.add_edge("format_response", END)

    return builder.compile(checkpointer=checkpointer)


__all__ = ["create_graph"]
