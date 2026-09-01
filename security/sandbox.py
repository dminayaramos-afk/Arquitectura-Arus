"""
ARUS
Sandbox
"""

from __future__ import annotations

from pathlib import Path


class Sandbox:

    def __init__(self):

        self.allowed = [

            Path("/home/damian/ARUS").resolve(),

            Path("/tmp").resolve(),

        ]


    def check(
        self,
        path: str,
    ):

        try:

            target = Path(path).expanduser().resolve()

        except Exception:

            return False

        for base in self.allowed:

            try:

                target.relative_to(base)
                return True

            except ValueError:

                pass

        return False
