"""
ARUS
Task
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:

    name: str

    arguments: dict = field(default_factory=dict)

    status: str = "pending"

    result: object = None
