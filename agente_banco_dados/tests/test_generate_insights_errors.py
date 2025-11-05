"""Tests covering error handling paths in the insights generation node."""

from __future__ import annotations

from typing import Dict

import pytest

from agente_banco_dados.config import ConfigurationError
from agente_banco_dados.utils import nodes
from agente_banco_dados.utils.nodes import render_sales_report


@pytest.fixture()
def minimal_state() -> Dict[str, object]:
    """Baseline state for invoking the insights node."""

    return {
        "top_products": [
            {"product_name": "Notebook Pro", "total_quantity": 20, "total_revenue": 45000.0},
        ],
        "top_sellers": [
            {"seller_name": "Alice Alves", "region": "SP", "total_quantity": 25, "total_revenue": 30000.0},
        ],
        "metadata": {},
    }


def test_generate_insights_node_handles_missing_api_key(monkeypatch, minimal_state):
    """Missing API key must produce actionable guidance and log llm_error metadata."""

    def fake_generate(*_args, **_kwargs):
        raise ConfigurationError("Credencial inexistente.")

    monkeypatch.setattr(nodes, "generate_sales_insights", fake_generate)

    partial_state = nodes.generate_insights_node(minimal_state)
    assert partial_state["metadata"]["llm_error"] == "Credencial inexistente."
    assert "fallback_message" in partial_state
    assert "Configure a variável GEMINI_API_KEY" in partial_state["fallback_message"]

    final_state = {**minimal_state, **partial_state}
    rendered = render_sales_report(final_state)
    markdown = rendered["report_markdown"]
    assert "Configure a variável GEMINI_API_KEY" in markdown
    assert rendered["metadata"]["llm_error"] == "Credencial inexistente."


def test_generate_insights_node_handles_generic_failure(monkeypatch, minimal_state):
    """Unexpected provider failures must inform the user and register the exception."""

    def fake_generate(*_args, **_kwargs):
        raise RuntimeError("Timeout ao chamar serviço.")

    monkeypatch.setattr(nodes, "generate_sales_insights", fake_generate)

    partial_state = nodes.generate_insights_node(minimal_state)
    assert partial_state["metadata"]["llm_error"] == "Timeout ao chamar serviço."
    assert "tente novamente" in partial_state["fallback_message"].lower()

    final_state = {**minimal_state, **partial_state}
    rendered = render_sales_report(final_state)
    markdown = rendered["report_markdown"]
    assert "Ocorreu um erro ao acessar o serviço de IA" in markdown
    assert rendered["metadata"]["llm_error"] == "Timeout ao chamar serviço."
