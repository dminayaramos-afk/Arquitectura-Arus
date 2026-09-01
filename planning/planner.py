"""
ARUS
Planner

Convierte una petición en un plan ejecutable.

La lógica inicial es deliberadamente conservadora:
las operaciones conocidas se convierten en pasos de ToolAgent.
"""

from __future__ import annotations

import re

from planning.plan import Plan


class Planner:

    def __init__(self, tools=None):

        self.tools = tools

    def plan(self, message: str) -> Plan:

        message = str(message).strip()

        plan = Plan(
            goal=message
        )

        # Operaciones matemáticas simples.
        patterns = [
            (
                r"^suma\s+(.+?)\s+(.+?)$",
                "suma",
            ),
            (
                r"^resta\s+(.+?)\s+(.+?)$",
                "resta",
            ),
            (
                r"^multiplica\s+(.+?)\s+(.+?)$",
                "multiplica",
            ),
            (
                r"^divide\s+(.+?)\s+(.+?)$",
                "divide",
            ),
        ]

        for pattern, action in patterns:

            match = re.match(
                pattern,
                message,
                re.IGNORECASE,
            )

            if match:

                plan.add_step(
                    action,
                    {
                        "a": match.group(1),
                        "b": match.group(2),
                    },
                )

                return plan

        return plan
