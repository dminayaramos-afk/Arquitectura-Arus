"""
ARUS
Planner
"""

from __future__ import annotations

from brain.task import Task


class Planner:

    def create_plan(
        self,
        tool: str,
        arguments: dict,
    ):

        return [
            Task(
                name=tool,
                arguments=arguments,
            )
        ]
