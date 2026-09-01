"""
ARUS
Calculator Tool

Estaba vacío (0 bytes) — ToolManager lo cargaba sin error pero no
registraba ninguna herramienta "calculator", así que Ollama nunca
podía ofrecérsela al modelo como function-calling (punto 16 del
prompt maestro: "Cálculo -> Calculator").

Evaluación segura por AST (mismo enfoque ya probado en
agents/tool_agent.py para "calc "), sin usar eval().
"""

from __future__ import annotations

import ast
import operator

from tools.base_tool import BaseTool

_OPERADORES = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _evaluar_nodo(node):

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Solo se permiten números.")

    if isinstance(node, ast.BinOp):
        op = _OPERADORES.get(type(node.op))
        if op is None:
            raise ValueError("Operación no permitida.")
        return op(_evaluar_nodo(node.left), _evaluar_nodo(node.right))

    if isinstance(node, ast.UnaryOp):
        op = _OPERADORES.get(type(node.op))
        if op is None:
            raise ValueError("Operación no permitida.")
        return op(_evaluar_nodo(node.operand))

    raise ValueError("Expresión no permitida.")


class CalculatorTool(BaseTool):

    name = "calculator"

    description = "Evalúa una expresión matemática (+ - * / ** paréntesis)."

    parameters = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Expresión matemática, por ejemplo '2 + 2 * 3'.",
            },
        },
        "required": ["expression"],
    }

    def execute(self, expression: str):

        try:
            resultado = _evaluar_nodo(ast.parse(expression, mode="eval").body)
        except Exception as e:
            return f"Error de cálculo: {e}"

        return str(resultado)
