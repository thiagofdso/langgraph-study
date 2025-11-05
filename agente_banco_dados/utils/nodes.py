"""LangGraph nodes for collecting metrics and rendering the SQLite sales report."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from agente_banco_dados.config import DB_PATH, ConfigurationError
from agente_banco_dados.reporting import (
    build_markdown_report,
    query_top_products,
    query_top_sellers,
)
from agente_banco_dados.state import (
    InsightSummary,
    ProductSummary,
    ReportState,
    SellerSummary,
)
from agente_banco_dados.utils.llm import generate_sales_insights


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
    processed_records = len(products_raw) + len(sellers_raw)
    return {
        "top_products": _normalise_products(products_raw),
        "top_sellers": _normalise_sellers(sellers_raw),
        "processed_records": processed_records,
        "metadata": {
            "processed_records": processed_records,
            "data_source": str(DB_PATH),
        },
    }


def generate_insights_node(state: ReportState) -> Dict[str, object]:
    """Invoke the Gemini model to build narrative insights anchored in the sales metrics."""

    products = state.get("top_products", [])
    sellers = state.get("top_sellers", [])
    metadata = {**state.get("metadata", {})}
    if "processed_records" in state:
        metadata.setdefault("processed_records", state["processed_records"])
    metadata.setdefault("data_source", str(DB_PATH))

    try:
        insights_text, latency = generate_sales_insights(products, sellers)
        insights = _structure_insights(insights_text)
        metadata["llm_latency_seconds"] = latency
        return {
            "insights": insights,
            "llm_latency_seconds": latency,
            "metadata": metadata,
        }
    except ConfigurationError as exc:
        friendly = (
            "Não foi possível gerar insights automáticos.\n"
            f"Motivo: {exc}\n"
            "Configure a variável GEMINI_API_KEY e tente novamente."
        )
        metadata["llm_error"] = str(exc)
        return {
            "insights": [],
            "llm_latency_seconds": 0.0,
            "metadata": metadata,
            "fallback_message": friendly,
        }
    except Exception as exc:  # pragma: no cover - exercised via dedicated tests
        friendly = (
            "Ocorreu um erro ao acessar o serviço de IA. "
            "Tente novamente em instantes ou verifique sua conexão."
        )
        metadata["llm_error"] = str(exc)
        return {
            "insights": [],
            "llm_latency_seconds": 0.0,
            "metadata": metadata,
            "fallback_message": friendly,
        }


def render_sales_report(state: ReportState) -> Dict[str, object]:
    """Render the Markdown report given the pre-populated sales metrics."""

    if "top_products" not in state or "top_sellers" not in state:
        raise KeyError("Sales metrics must be collected before rendering the report.")

    report_markdown = build_markdown_report(state["top_products"], state["top_sellers"])

    insight_lines = []
    if state.get("fallback_message"):
        insight_lines.append(state["fallback_message"])
    elif state.get("insights"):
        for insight in state["insights"]:
            insight_lines.append(f"- {insight['rationale']}")
    else:
        insight_lines.append(
            "Não foi possível gerar insights adicionais no momento. Verifique os dados e tente novamente."
        )

    generated_at = datetime.now(tz=timezone.utc).isoformat()
    sections = [
        report_markdown,
        "",
        "## Insights gerados pela IA",
        "\n".join(insight_lines),
        "",
        f"*Gerado em {generated_at}*",
    ]

    metadata = {**state.get("metadata", {}), "generated_at": generated_at}
    metadata.setdefault("data_source", str(DB_PATH))
    if "processed_records" in state:
        metadata.setdefault("processed_records", state["processed_records"])
    if "llm_latency_seconds" in state:
        metadata.setdefault("llm_latency_seconds", state["llm_latency_seconds"])

    return {
        "report_markdown": "\n".join(sections).strip(),
        "metadata": metadata,
    }


def _structure_insights(raw_text: str) -> List[InsightSummary]:
    """Split the model response into structured insight summaries."""

    cleaned = raw_text.strip()
    if not cleaned:
        return []

    blocks: List[str] = []
    for chunk in cleaned.split("\n\n"):
        normalised = chunk.strip()
        if normalised:
            blocks.append(normalised)

    if not blocks:
        blocks = [cleaned]

    structured: List[InsightSummary] = []
    for index, block in enumerate(blocks[:3], start=1):
        structured.append(
            InsightSummary(
                headline=f"Insight {index}",
                rationale=block,
                supporting_metrics=[],
            )
        )
    return structured


__all__ = [
    "load_sales_metrics",
    "generate_insights_node",
    "render_sales_report",
]
