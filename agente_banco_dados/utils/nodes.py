"""LangGraph nodes for collecting metrics and rendering the SQLite sales report."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from agente_banco_dados.reporting import (
    build_markdown_report,
    query_top_products,
    query_top_sellers,
)
from agente_banco_dados.state import ProductSummary, ReportState, SellerSummary


def _normalise_products(raw_products: List[Dict[str, object]]) -> List[ProductSummary]:
    """Convert raw rows from SQLite into the typed product summary structure."""

    summaries: List[ProductSummary] = []
    for row in raw_products:
        summaries.append(
            ProductSummary(
                product_name=str(row["product_name"]),
                total_quantity=int(row["total_quantity"]),
                total_revenue=float(row["total_revenue"]),
            )
        )
    return summaries


def _normalise_sellers(raw_sellers: List[Dict[str, object]]) -> List[SellerSummary]:
    """Convert raw rows from SQLite into the typed seller summary structure."""

    summaries: List[SellerSummary] = []
    for row in raw_sellers:
        summaries.append(
            SellerSummary(
                seller_name=str(row["seller_name"]),
                region=str(row["region"]),
                total_quantity=int(row["total_quantity"]),
                total_revenue=float(row["total_revenue"]),
            )
        )
    return summaries


def load_sales_metrics(_: ReportState) -> Dict[str, object]:
    """Fetch top products and sellers from the local SQLite database."""

    products_raw = query_top_products()
    sellers_raw = query_top_sellers()
    return {
        "top_products": _normalise_products(products_raw),
        "top_sellers": _normalise_sellers(sellers_raw),
    }


def render_sales_report(state: ReportState) -> Dict[str, object]:
    """Render the Markdown report given the pre-populated sales metrics."""

    if "top_products" not in state or "top_sellers" not in state:
        raise KeyError("Sales metrics must be collected before rendering the report.")

    report_markdown = build_markdown_report(state["top_products"], state["top_sellers"])
    return {
        "report_markdown": report_markdown,
        "metadata": {
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        },
    }


__all__ = [
    "load_sales_metrics",
    "render_sales_report",
]
