"""State contracts shared across the SQLite sales agent workflow."""

from __future__ import annotations

from typing import Any, Dict, List
from typing_extensions import TypedDict


class ProductSummary(TypedDict):
    """Aggregated metrics for a single product within the report."""

    product_name: str
    total_quantity: int
    total_revenue: float


class SellerSummary(TypedDict):
    """Aggregated metrics for a seller, enriched with the declared region."""

    seller_name: str
    region: str
    total_quantity: int
    total_revenue: float


class ReportState(TypedDict, total=False):
    """LangGraph state exchanged between nodes during report generation."""

    top_products: List[ProductSummary]
    top_sellers: List[SellerSummary]
    report_markdown: str
    metadata: Dict[str, Any]
