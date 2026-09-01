"""
ARUS AI Chat Skill
"""

from __future__ import annotations

from ai.model_manager import ModelManager
from skills.base_skill import BaseSkill


class AIChatSkill(BaseSkill):


    name = "ai"


    def __init__(self):

        self.model = ModelManager()



    def execute(
        self,
        message: str,
        history=None,
    ):

        return self.model.generate(
            message,
            history,
        )
