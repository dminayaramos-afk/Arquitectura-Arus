"""
Research Agent
"""

from brain.agent import Agent


class ResearchAgent(Agent):

    def __init__(self):

        super().__init__(
            name="Researcher",
            role="research",
            description="Especialista en búsqueda y análisis de información.",
            capabilities=[
                "search",
                "web",
                "web_reader",
                "github_search",
            ],
        )
