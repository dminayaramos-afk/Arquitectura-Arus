"""
ARUS
Plan Result
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlanResult:

    success: bool = True

    tasks: list = field(default_factory=list)

    final_result: object = None

    errors: list = field(default_factory=list)
