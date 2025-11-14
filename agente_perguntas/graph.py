"""LangGraph builder for agente_perguntas."""

from __future__ import annotations

from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from structlog.stdlib import BoundLogger

from agente_perguntas.config import AppConfig
from agente_perguntas.state import AgentState
from agente_perguntas.utils.logging import setup_logging
from agente_perguntas.utils.nodes import evaluate_question
from agente_perguntas.utils.prompts import get_faq_entries

CompiledGraph = Any


def build_graph(
    app_config: AppConfig,
    logger: BoundLogger,
    *,
    checkpointer: InMemorySaver | None = None,
) -> CompiledGraph:
    """Compile and return the LangGraph workflow for the FAQ agent."""

    faq_entries = get_faq_entries()
    builder = StateGraph(AgentState)

    def _evaluate(state: AgentState) -> AgentState:
        return evaluate_question(
            state,
            settings=app_config,
            logger=logger,
            faq_entries=faq_entries,
        )

    builder.add_node("evaluate", _evaluate)
    builder.add_edge(START, "evaluate")
    builder.add_edge("evaluate", END)

    if checkpointer is not None:
        return builder.compile(checkpointer=checkpointer)
    return builder.compile()


def create_app(checkpointer: InMemorySaver | None = None) -> CompiledGraph:
    """Factory used by LangGraph runtime to instantiate the FAQ workflow."""

    app_config = AppConfig.load()
    logger = setup_logging(enable_file_handler=False)
    return build_graph(app_config, logger, checkpointer=checkpointer)


__all__ = ["build_graph", "create_app"]
