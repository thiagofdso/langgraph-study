"""Entry point for the SQLite sales agent."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from agente_banco_dados.db_init import initialize_database
from agente_banco_dados.reporting import (
    build_markdown_report,
    query_top_products,
    query_top_sellers,
)


class ReportState(TypedDict, total=False):
    """State passed between LangGraph nodes."""

    top_products: list[dict[str, float | str]]
    top_sellers: list[dict[str, float | str]]
    report_markdown: str


def _build_graph() -> Any:
    """Construct the LangGraph workflow for report generation."""
    graph_builder = StateGraph(ReportState)

    def collect_metrics(_: ReportState) -> ReportState:
        return {
            "top_products": query_top_products(),
            "top_sellers": query_top_sellers(),
        }

    def render_markdown(state: ReportState) -> ReportState:
        return {
            "report_markdown": build_markdown_report(
                state["top_products"], state["top_sellers"]
            )
        }

    graph_builder.add_node("collect_metrics", collect_metrics)
    graph_builder.add_node("render_markdown", render_markdown)
    graph_builder.add_edge(START, "collect_metrics")
    graph_builder.add_edge("collect_metrics", "render_markdown")
    graph_builder.add_edge("render_markdown", END)
    return graph_builder.compile()


REPORT_GRAPH = _build_graph()


def generate_report() -> str:
    """Run the LangGraph workflow and return the markdown report."""
    result = REPORT_GRAPH.invoke({})
    return result["report_markdown"]


def main() -> None:
    """Run the study agent once."""
    counts = initialize_database()
    print(
        "Database ready with "
        f"{counts['products']} products, "
        f"{counts['sellers']} sellers, "
        f"{counts['sales']} sales records."
    )
    print("Relatório gerado exclusivamente a partir do banco SQLite local.")
    report_md = generate_report()
    print(report_md)


if __name__ == "__main__":
    main()
