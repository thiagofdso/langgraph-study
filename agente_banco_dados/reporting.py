"""Reporting helpers for summarising local SQLite sales data."""

from __future__ import annotations

from typing import Iterable, Sequence

from agente_banco_dados.config import TOP_N_PRODUCTS, TOP_N_SELLERS
from agente_banco_dados.db_init import get_connection


def query_top_products(limit: int = TOP_N_PRODUCTS) -> list[dict[str, float | str]]:
    """Return the top products ordered by quantity sold."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                p.name AS product_name,
                SUM(s.quantity) AS total_quantity,
                ROUND(SUM(s.quantity * s.unit_price), 2) AS total_revenue
            FROM sales s
            JOIN products p ON p.product_id = s.product_id
            GROUP BY p.product_id
            ORDER BY total_quantity DESC, total_revenue DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def query_top_sellers(limit: int = TOP_N_SELLERS) -> list[dict[str, float | str]]:
    """Return the top sellers ordered by total revenue."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                se.name AS seller_name,
                COALESCE(se.region, 'Sem região') AS region,
                SUM(sa.quantity) AS total_quantity,
                ROUND(SUM(sa.quantity * sa.unit_price), 2) AS total_revenue
            FROM sales sa
            JOIN sellers se ON se.seller_id = sa.seller_id
            GROUP BY se.seller_id
            ORDER BY total_revenue DESC, total_quantity DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def _format_markdown_row(cells: Sequence[str], widths: Sequence[int]) -> str:
    """Return a markdown table row with padded cells."""
    padded = [cell.ljust(width) for cell, width in zip(cells, widths)]
    return "| " + " | ".join(padded) + " |"


def format_markdown_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    """Format a markdown table from headers and row values."""
    rows_list = [tuple(row) for row in rows]
    widths = [len(header) for header in headers]
    for row in rows_list:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]

    header_line = _format_markdown_row(headers, widths)
    separator = "| " + " | ".join("-" * width for width in widths) + " |"
    data_lines = [_format_markdown_row(row, widths) for row in rows_list]
    return "\n".join([header_line, separator, *data_lines]) if data_lines else "\n".join([header_line, separator])


def build_markdown_report(
    top_products: list[dict[str, float | str]],
    top_sellers: list[dict[str, float | str]],
) -> str:
    """Return the markdown report for top products and sellers."""
    product_rows = [
        (
            record["product_name"],
            str(int(record["total_quantity"])),
            f"R$ {record['total_revenue']:.2f}".replace(".", ",", 1)
        )
        for record in top_products
    ]

    seller_rows = [
        (
            record["seller_name"],
            record["region"],
            str(int(record["total_quantity"])),
            f"R$ {record['total_revenue']:.2f}".replace(".", ",", 1)
        )
        for record in top_sellers
    ]

    report_sections = [
        "# Relatório de Vendas Baseado em SQLite",
        "*Fonte: banco de dados local agente_banco_dados/data/sales.db*",
        "",
        "## Produtos mais vendidos",
        format_markdown_table(("Produto", "Quantidade", "Receita"), product_rows),
        "",
        "## Melhores vendedores",
        format_markdown_table(("Vendedor", "Região", "Quantidade", "Receita"), seller_rows),
    ]
    return "\n".join(section for section in report_sections if section is not None)

