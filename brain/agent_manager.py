"""
ARUS
Agent Manager
"""

from __future__ import annotations

from brain.agent import Agent


class AgentManager:

    def __init__(self):

        self.agents: dict[str, Agent] = {}

    def register(
        self,
        agent: Agent,
    ):

        self.agents[agent.name] = agent

    def unregister(
        self,
        name: str,
    ):

        self.agents.pop(name, None)

    def get(
        self,
        name: str,
    ) -> Agent | None:

        return self.agents.get(name)

    def all(self):

        return list(
            self.agents.values()
        )

    def active(self):

        return [
            agent
            for agent in self.agents.values()
            if agent.active
        ]

    def find_by_capability(
        self,
        capability: str,
    ) -> list[Agent]:

        return [
            agent
            for agent in self.active()
            if agent.can(capability)
        ]

    def best(
        self,
        capability: str,
    ) -> Agent | None:

        agents = self.find_by_capability(
            capability
        )

        if agents:
            return agents[0]

        return None
