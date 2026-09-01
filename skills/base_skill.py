"""
ARUS
Base Skill
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSkill(ABC):

    name = "base"

    @abstractmethod
    def execute(self, message: str) -> str:
        pass
