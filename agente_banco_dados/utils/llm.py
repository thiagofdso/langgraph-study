"""Helpers responsible for invoking the Gemini model to generate sales insights."""

from __future__ import annotations

from time import perf_counter
from typing import Sequence, Tuple

from langchain_core.messages import HumanMessage, SystemMessage

from agente_banco_dados.config import ConfigurationError, config
from agente_banco_dados.state import ProductSummary, SellerSummary
from agente_banco_dados.utils.prompts import SALES_INSIGHT_SYSTEM, build_sales_prompt


def generate_sales_insights(
    products: Sequence[ProductSummary],
    sellers: Sequence[SellerSummary],
) -> Tuple[str, float]:
    """Invoke the configured Gemini model and return the narrative plus call latency in seconds."""

    llm = config.create_llm()
    prompt = build_sales_prompt(products, sellers)
    start = perf_counter()
    response = llm.invoke(
        [
            SystemMessage(content=SALES_INSIGHT_SYSTEM),
            HumanMessage(content=prompt),
        ]
    )
    latency = perf_counter() - start
    content = getattr(response, "content", str(response))
    return content or "", latency
