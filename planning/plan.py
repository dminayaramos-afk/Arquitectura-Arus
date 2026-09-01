"""
ARUS
Plan

Representa un plan de ejecución generado por el Planner.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlanStep:

    action: str
    arguments: dict = field(default_factory=dict)


@dataclass
class Plan:

    goal: str
    steps: list[PlanStep] = field(default_factory=list)

    def add_step(
        self,
        action: str,
        arguments: dict | None = None,
    ):

        self.steps.append(
            PlanStep(
                action=action,
                arguments=arguments or {},
            )
        )

        return self

    def is_empty(self):

        return len(self.steps) == 0
