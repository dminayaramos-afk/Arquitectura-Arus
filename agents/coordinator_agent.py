"""
Coordinator Agent
"""

from __future__ import annotations

from brain.agent import Agent
from brain.message import Message
from brain.message_bus import MessageBus


class CoordinatorAgent(Agent):

    def __init__(self):

        super().__init__(
            name="Coordinator",
            role="coordinator",
            description="Coordina el trabajo entre agentes.",
            capabilities=[
                "coordinate",
            ],
        )

        self.router = None
        self.bus = MessageBus()

    def set_router(self, router):
        self.router = router

    def delegate(
        self,
        capability: str,
        task: str,
    ):

        if self.router is None:
            raise RuntimeError("Router no configurado")

        agent = self.router.route(capability)

        if agent is None:
            return None

        self.bus.send(
            Message(
                sender=self.name,
                receiver=agent.name,
                content=task,
            )
        )

        return agent.name

    def inbox(
        self,
        agent_name: str,
    ):

        return self.bus.receive(agent_name)
