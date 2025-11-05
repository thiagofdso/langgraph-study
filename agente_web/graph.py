"""Graph assembly for the agente_web project."""

from __future__ import annotations

from functools import partial

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agente_web.config import config
from agente_web.state import GraphState
from agente_web.utils.nodes import buscar, resumir


def create_app():
    """Compile the agente_web workflow using global configuration."""

    search_tool = config.create_search_tool()
    tool_runner = ToolNode([search_tool], name="buscar_tool")
    summary_model = config.create_model()

    builder = StateGraph(GraphState)
    builder.add_node(
        "buscar",
        partial(
            buscar,
            tool_runner=tool_runner,
            tool_name=search_tool.name,
            max_results=config.tavily_max_results,
        ),
    )
    builder.add_node(
        "resumir",
        partial(
            resumir,
            model=summary_model,
            max_sources=config.summary_max_sources,
        ),
    )

    builder.add_edge(START, "buscar")
    builder.add_edge("buscar", "resumir")
    builder.add_edge("resumir", END)

    return builder.compile(checkpointer=config.create_checkpointer())


app = create_app()
