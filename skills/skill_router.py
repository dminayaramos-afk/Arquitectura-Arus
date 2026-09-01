"""
ARUS
Skill Router

Traduce intenciones a habilidades reales.
"""

from __future__ import annotations


class SkillRouter:


    def __init__(self):

        self.rules = {

            "chat": "chat",

            "hello": "chat",

            "hola": "chat",

            "coding": "ai",

            "code": "ai",

            "python": "ai",

            "knowledge": "ai",

            "question": "ai",

            "ai": "ai",

        }


    def resolve(
        self,
        intent: str,
    ):

        intent = intent.lower()


        return self.rules.get(
            intent,
            "chat"
        )
