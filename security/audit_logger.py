"""
ARUS
Audit Logger
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime


class AuditLogger:

    def __init__(self):

        self.file = Path("logs/audit.log")

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


    def log(
        self,
        tool: str,
        arguments,
        result,
    ):

        with self.file.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                f"[{datetime.now()}]\n"
            )

            f.write(
                f"Tool: {tool}\n"
            )

            f.write(
                f"Arguments: {arguments}\n"
            )

            f.write(
                f"Result: {str(result)[:500]}\n"
            )

            f.write(
                "-" * 80 + "\n"
            )
