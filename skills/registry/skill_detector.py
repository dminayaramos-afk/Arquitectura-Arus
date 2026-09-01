"""
ARUS
Skill Detector

Detecta clases Skill dentro de módulos.
"""

from __future__ import annotations

import inspect

from skills.base_skill import BaseSkill


class SkillDetector:


    def detect(self, module):

        found = []


        for name, obj in inspect.getmembers(module):

            if (
                inspect.isclass(obj)
                and issubclass(obj, BaseSkill)
                and obj is not BaseSkill
            ):

                found.append(obj)


        return found
