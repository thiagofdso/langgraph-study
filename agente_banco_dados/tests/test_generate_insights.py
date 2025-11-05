"""Tests for the generate_insights_node behaviour."""

from __future__ import annotations

from typing import Dict

import pytest

from agente_banco_dados.utils import nodes


@pytest.fixture()
def sample_state() -> Dict[str, object]:
    """Return a minimal state structure consumed by generate_insights_node."""

    return {
        "top_products": [
            {"product_name": "Notebook Pro", "total_quantity": 20, "total_revenue": 45000.0},
            {"product_name": "Mouse Gamer", "total_quantity": 15, "total_revenue": 3750.0},
        ],
        "top_sellers": [
            {"seller_name": "Alice Alves", "region": "SP", "total_quantity": 25, "total_revenue": 30000.0},
            {"seller_name": "Bruno Barros", "region": "RJ", "total_quantity": 18, "total_revenue": 22000.0},
        ],
        "metadata": {},
    }


def test_generate_insights_node_returns_three_blocks(monkeypatch, sample_state):
    """The node must structure up to three insight blocks with latency metadata."""

    def fake_generate(products, sellers):
        assert products == sample_state["top_products"]
        assert sellers == sample_state["top_sellers"]
        return (
            "1. Tendência: Notebook Pro mantém receita R$ 45000,00.\n\n"
            "2. Risco: Mouse Gamer caiu para 15 unidades, monitorar descontos.\n\n"
            "3. Ação: Incentivar Alice Alves (SP) a vender combos premium.",
            0.42,
        )

    monkeypatch.setattr(nodes, "generate_sales_insights", fake_generate)

    result = nodes.generate_insights_node(sample_state)

    assert "insights" in result
    assert len(result["insights"]) == 3
    assert result["insights"][0]["headline"] == "Insight 1"
    assert "Notebook Pro" in result["insights"][0]["rationale"]
    assert result["llm_latency_seconds"] == pytest.approx(0.42)
    assert result["metadata"]["llm_latency_seconds"] == pytest.approx(0.42)
