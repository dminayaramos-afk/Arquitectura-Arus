"""
ARUS
Context Builder

Construye prompts con contexto.
"""

from __future__ import annotations


class ContextBuilder:


    def build(self, messages):

        prompt = ""

        for message in messages:

            role = message["role"]

            content = message["content"]

            prompt += (
                f"{role}: {content}\n"
            )


        return prompt
