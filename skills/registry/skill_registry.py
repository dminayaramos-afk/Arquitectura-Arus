"""
ARUS
Skill Registry

Registro central de habilidades.
"""

from __future__ import annotations


class SkillRegistry:


    def __init__(self):

        self.skills = {}


    def register(
        self,
        skill,
    ):

        self.skills[skill.name] = skill


    def get(
        self,
        name: str,
    ):

        return self.skills.get(name)


    def all(self):

        return self.skills.values()
