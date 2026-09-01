"""
Coder Agent
"""

from brain.agent import Agent


class CoderAgent(Agent):

    def __init__(self):

        super().__init__(
            name="Coder",
            role="programmer",
            description="Especialista en programación.",
            capabilities=[
                "python",
                "git",
                "debug",
            ],
        )
