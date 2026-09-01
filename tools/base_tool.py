"""
ARUS
Base Tool
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTool(ABC):

    name = "base"

    description = "Base tool"

    parameters = {
        "type": "object",
        "properties": {}
    }


    @abstractmethod
    def execute(
        self,
        *args,
        **kwargs,
    ):
        pass


    def schema(self):

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
