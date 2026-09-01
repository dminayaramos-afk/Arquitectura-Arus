"""
ARUS
Plan Executor

Ejecuta un Plan mediante el sistema de Tools/Agents disponible.
"""

from __future__ import annotations


class PlanExecutor:

    def __init__(self, tool_agent):

        self.tool_agent = tool_agent

    def execute(self, plan):

        results = []

        for step in plan.steps:

            arguments = step.arguments

            a = arguments.get("a")
            b = arguments.get("b")

            message = (
                f"{step.action} {a} {b}"
            )

            from agents.agent_request import AgentRequest

            result = self.tool_agent.execute(
                AgentRequest(
                    message=message
                )
            )

            results.append(result)

        return results
