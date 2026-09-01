"""
ARUS
JSON Validator
"""

from __future__ import annotations

import json


class JsonValidator:

    def parse(self, text: str):

        try:
            return json.loads(text)

        except Exception:
            return None
