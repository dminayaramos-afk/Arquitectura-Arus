"""
ARUS
Skill Manager
"""

from __future__ import annotations

from skills.registry.skill_bootstrap import SkillBootstrap
from skills.skill_router import SkillRouter



class SkillManager:


    def __init__(self):

        bootstrap = SkillBootstrap()

        self.registry = bootstrap.initialize()

        self.router = SkillRouter()



    def execute(
        self,
        intent: str,
        message: str,
        history=None,
    ):


        skill_name = self.router.resolve(
            intent
        )


        skill = self.registry.get(
            skill_name
        )


        if skill is None:

            return (
                "Skill no encontrada: "
                + skill_name
            )


        return skill.execute(
            message,
            history,
        )
