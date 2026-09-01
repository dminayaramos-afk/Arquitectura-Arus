
"""
ARUS
Agent Manager
"""

from arus.laboratory.agents import Agent
from arus.laboratory.repositories import AgentRepository


class AgentManager:


    def __init__(self):

        self._agents = {}

        self.repository = AgentRepository()



    def create(
        self,
        name,
        role=""
    ):

        agent = Agent(
            name,
            role
        )

        self._agents[name] = agent

        self.repository.save(agent)

        return agent



    def get(
        self,
        name
    ):

        return self._agents.get(name)



    def delete(
        self,
        name
    ):

        if name in self._agents:

            del self._agents[name]



    def list(self):

        return list(
            self._agents.values()
        )



    def count(self):

        return len(
            self._agents
        )



    def start(
        self,
        name
    ):

        agent = self.get(name)

        if agent:

            agent.start()

            self.repository.save(agent)

        return agent



    def stop(
        self,
        name
    ):

        agent = self.get(name)

        if agent:

            agent.stop()

            self.repository.save(agent)

        return agent
