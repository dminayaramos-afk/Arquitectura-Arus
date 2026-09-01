"""
ARUS
Agent Registry
"""

from __future__ import annotations

from typing import Dict, List

from agents.base_agent import BaseAgent


class AgentRegistry:

    def __init__(self):

        self._agents: Dict[str, BaseAgent] = {}

    def register(
        self,
        name: str,
        agent: BaseAgent,
    ):

        self._agents[name] = agent

    def unregister(
        self,
        name: str,
    ):

        self._agents.pop(name, None)

    def get(
        self,
        name: str,
    ):

        return self._agents.get(name)

    def all(self) -> List[BaseAgent]:

        return list(
            self._agents.values()
        )

    def names(self) -> List[str]:

        return sorted(
            self._agents.keys()
        )

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._agents

    def clear(self):

        self._agents.clear()

    def count(self):

        return len(
            self._agents
        )
