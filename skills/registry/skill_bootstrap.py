"""
ARUS
Skill Bootstrap

Inicialización automática de habilidades.
"""

from __future__ import annotations

from skills.registry.skill_discovery import SkillDiscovery
from skills.registry.skill_registry import SkillRegistry


class SkillBootstrap:


    def __init__(self):

        self.registry = SkillRegistry()

        self.discovery = SkillDiscovery()


    def initialize(self):

        skill_classes = self.discovery.discover()


        for skill_class in skill_classes:

            skill_instance = skill_class()

            self.registry.register(
                skill_instance
            )


        return self.registry
