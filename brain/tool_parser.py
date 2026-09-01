"""
ARUS
Tool Parser
"""

from __future__ import annotations

from utils.json_validator import JsonValidator


class ToolParser:

    def __init__(self):

        self.validator = JsonValidator()

    def parse(
        self,
        text: str,
    ):

        data = self.validator.parse(text)

        if data is None:
            return None

        if not isinstance(data, dict):
            return None

        tool = data.get("tool")

        if not tool:
            return None

        arguments = {
            k: v
            for k, v in data.items()
            if k != "tool"
        }

        return tool, arguments
