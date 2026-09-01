"""
ARUS
Agent Router
"""

from __future__ import annotations

from agents.agent_registry import AgentRegistry


class AgentRouter:

    def __init__(self):

        self.registry = AgentRegistry()
        self.registry.load()

        coordinator = self.registry.get(
            "Coordinator"
        )

        if coordinator is not None:
            coordinator.set_router(self)


    def route(
        self,
        capability: str,
    ):

        for agent in self.registry.all():

            if agent.active and agent.can(capability):

                return agent

        return None


    def explain(
        self,
        capability: str,
    ):

        agent = self.route(capability)

        if agent is None:

            return f"No existe un agente para '{capability}'."

        return (
            f"'{capability}' será ejecutado por "
            f"{agent.name} ({agent.role})"
        )
