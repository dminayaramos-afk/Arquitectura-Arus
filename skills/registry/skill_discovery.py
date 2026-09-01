"""
ARUS
Skill Discovery Engine
"""

from __future__ import annotations

from skills.registry.skill_detector import SkillDetector
from skills.registry.skill_loader import SkillLoader


class SkillDiscovery:


    def __init__(self):

        self.loader = SkillLoader()

        self.detector = SkillDetector()


    def discover(self):

        skills = []


        modules = self.loader.discover()


        for module in modules:

            classes = self.detector.detect(
                module
            )

            skills.extend(classes)


        return skills
