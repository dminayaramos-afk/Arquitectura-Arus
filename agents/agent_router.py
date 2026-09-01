"""
ARUS
Agent Router
"""

from __future__ import annotations

from agents.agent_request import AgentRequest
from agents.agent_registry import AgentRegistry


class AgentRouter:

    def __init__(
        self,
        registry: AgentRegistry,
    ):

        self.registry = registry

    def route(
        self,
        request: AgentRequest,
    ):

        for agent in self.registry.all():

            try:

                if agent.can_handle(
                    request
                ):
                    return agent

            except Exception:

                continue

        return None
