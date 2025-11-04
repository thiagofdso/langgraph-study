"""Tool implementations used by agente_tool."""

from __future__ import annotations

from langchain.tools import tool


@tool("calculator", description="Performs arithmetic calculations. Use this for any math problems.")
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions using Python's eval, mirroring the legacy behavior."""

    try:
        result = eval(expression)
    except Exception as exc:  # noqa: S307 - intencional para compatibilidade legada
        return f"Error: {exc}"
    return str(result)


__all__ = ["calculator"]
