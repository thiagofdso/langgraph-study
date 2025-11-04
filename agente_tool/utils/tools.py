"""Tool implementations used by agente_tool."""

from __future__ import annotations

import ast
import operator
from typing import Union

from langchain.tools import tool

ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

AllowedNode = Union[ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant]


class CalculatorError(ValueError):
    """Raised when the calculator receives an invalid expression."""


def _eval_node(node: ast.AST) -> float:
    """Recursively evaluate a sanitized AST expression."""

    if isinstance(node, ast.Expression):
        return _eval_node(node.body)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise CalculatorError("Apenas números são permitidos na expressão.")

    if isinstance(node, ast.BinOp):
        operator_fn = ALLOWED_BINARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise CalculatorError("Operação matemática não suportada.")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        try:
            return operator_fn(left, right)
        except ZeroDivisionError as exc:  # pragma: no cover - tratado em testes
            raise CalculatorError("Divisão por zero não é permitida.") from exc

    if isinstance(node, ast.UnaryOp):
        operator_fn = ALLOWED_UNARY_OPERATORS.get(type(node.op))
        if operator_fn is None:
            raise CalculatorError("Operação unária não suportada.")
        operand = _eval_node(node.operand)
        return operator_fn(operand)

    raise CalculatorError("Expressão matemática inválida.")


def _sanitize_expression(expression: str) -> str:
    """Normalize whitespace and decimal separators before evaluation."""

    cleaned = expression.replace(",", ".")
    cleaned = cleaned.strip()
    if not cleaned:
        raise CalculatorError("Forneça uma expressão para ser avaliada.")
    return cleaned


@tool("calculator")
def calculator(expression: str) -> str:
    """Evaluate mathematical expressions using a safe AST-based sandbox."""

    sanitized = _sanitize_expression(expression)

    try:
        tree = ast.parse(sanitized, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError("Expressão malformada; revise a sintaxe.") from exc

    for node in ast.walk(tree):
        if isinstance(
            node,
            (
                ast.Call,
                ast.Attribute,
                ast.Name,
                ast.Subscript,
                ast.Dict,
                ast.List,
                ast.Tuple,
            ),
        ):
            raise CalculatorError(
                "Funções, variáveis ou estruturas complexas não são permitidas."
            )

    value = _eval_node(tree)
    if value.is_integer():
        return str(int(value))
    return str(round(value, 10)).rstrip("0").rstrip(".")


__all__ = ["calculator", "CalculatorError"]
