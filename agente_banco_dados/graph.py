"""LangGraph workflow definition for the SQLite sales reporting agent."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agente_banco_dados.state import ReportState
from agente_banco_dados.utils import (
    generate_insights_node,
    load_sales_metrics,
    render_sales_report,
)


def create_app():
    """Compile and return the LangGraph application responsible for report generation."""

    builder = StateGraph(ReportState)
    builder.add_node("load_sales_metrics", load_sales_metrics)
    builder.add_node("render_sales_report", render_sales_report)
    builder.add_node("generate_insights", generate_insights_node)

    builder.add_edge(START, "load_sales_metrics")
    builder.add_edge("load_sales_metrics", "generate_insights")
    builder.add_edge("generate_insights", "render_sales_report")
    builder.add_edge("render_sales_report", END)

    return builder.compile()


app = create_app()


__all__ = ["app", "create_app"]
