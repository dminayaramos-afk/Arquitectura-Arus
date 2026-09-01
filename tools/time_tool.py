"""
ARUS
Time Tool
"""

from __future__ import annotations

from datetime import datetime

from tools.base_tool import BaseTool


class TimeTool(BaseTool):

    name = "time"

    description = "Devuelve la fecha y hora actual."


    def execute(self):

        return datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )
