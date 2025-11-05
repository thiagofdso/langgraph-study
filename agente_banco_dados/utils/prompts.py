"""Prompt templates used to request narrative insights from the Gemini model."""

from __future__ import annotations

from textwrap import dedent
from typing import Iterable, Mapping


SALES_INSIGHT_SYSTEM = dedent(
    """
    Você é uma analista de vendas experiente.
    Gere insights em português brasileiro seguindo estas regras:
    - Sempre cite números exatos extraídos das tabelas fornecidas.
    - Produza exatamente três blocos na ordem: Tendências marcantes; Riscos ou quedas; Recomendações acionáveis.
    - Cada bloco deve mencionar quais produtos ou vendedores sustentam o argumento.
    - Quando não houver dados disponíveis, explique educadamente que é necessário revisar a consulta antes de gerar insights.
    """
).strip()


def build_sales_prompt(
    products: Iterable[Mapping[str, object]],
    sellers: Iterable[Mapping[str, object]],
) -> str:
    """Return the user prompt describing sales metrics that the Gemini model must analyse."""

    lines: list[str] = ["Dados consolidados a partir do banco SQLite local:", ""]

    lines.append("Produtos mais vendidos:")
    for item in products:
        lines.append(
            f"- {item['product_name']}: {int(item['total_quantity'])} unidades, receita R$ {float(item['total_revenue']):.2f}"
        )

    lines.append("")
    lines.append("Vendedores com maior receita:")
    for seller in sellers:
        lines.append(
            f"- {seller['seller_name']} ({seller['region']}): {int(seller['total_quantity'])} unidades, receita R$ {float(seller['total_revenue']):.2f}"
        )

    lines.append("")
    lines.append("Instrua a IA a gerar três blocos de resumo conforme as regras do prompt do sistema.")
    return "\n".join(lines)
