"""
ARUS
Base Agent
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Agent:

    name: str

    role: str

    description: str

    capabilities: list[str] = field(default_factory=list)

    active: bool = True

    def can(
        self,
        capability: str,
    ) -> bool:

        return capability in self.capabilities

    def enable(self):

        self.active = True

    def disable(self):

        self.active = False

    def info(self):

        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "capabilities": self.capabilities,
            "active": self.active,
        }
