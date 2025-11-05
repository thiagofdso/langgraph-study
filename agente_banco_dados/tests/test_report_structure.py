"""Integration-oriented tests validating the report structure."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Dict

from agente_banco_dados.utils.nodes import render_sales_report


def test_render_sales_report_includes_tables_and_timestamp():
    """The rendered Markdown must keep tables, insights section and timestamp metadata."""

    state: Dict[str, object] = {
        "top_products": [
            {"product_name": "Notebook Pro", "total_quantity": 20, "total_revenue": 45000.0},
        ],
        "top_sellers": [
            {"seller_name": "Alice Alves", "region": "SP", "total_quantity": 25, "total_revenue": 30000.0},
        ],
        "insights": [
            {
                "headline": "Insight 1",
                "rationale": "Notebook Pro mantém receita R$ 45000,00.",
                "supporting_metrics": [],
            }
        ],
        "metadata": {"processed_records": 2},
        "processed_records": 2,
        "llm_latency_seconds": 0.5,
    }

    result = render_sales_report(state)
    markdown = result["report_markdown"]

    assert "Relatório de Vendas Baseado em SQLite" in markdown
    assert "## Produtos mais vendidos" in markdown
    assert "## Melhores vendedores" in markdown
    assert "## Insights gerados pela IA" in markdown
    assert "- Notebook Pro mantém receita R$ 45000,00." in markdown
    assert re.search(r"\\*Gerado em .*\\*", markdown)

    metadata = result["metadata"]
    assert "generated_at" in metadata
    assert datetime.fromisoformat(metadata["generated_at"])
    assert metadata["processed_records"] == 2
    assert metadata["llm_latency_seconds"] == 0.5
