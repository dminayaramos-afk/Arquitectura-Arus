"""
ARUS
Base Agent
"""

from abc import ABC, abstractmethod

from agents.agent_request import AgentRequest
from agents.agent_response import AgentResponse


class BaseAgent(ABC):

    @abstractmethod
    def can_handle(
        self,
        request: AgentRequest,
    ) -> bool:
        pass

    @abstractmethod
    def execute(
        self,
        request: AgentRequest,
    ) -> AgentResponse:
        pass

    def metadata(self):

        return {
            "name": self.__class__.__name__,
            "version": "1.0"
        }

    def health(self):

        return True
