"""
ARUS Chat Skill
"""

from skills.base_skill import BaseSkill


class ChatSkill(BaseSkill):

    name = "chat"


    def execute(
        self,
        message: str,
        history=None,
    ):

        return "Has dicho: " + message
