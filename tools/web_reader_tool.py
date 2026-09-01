"""
ARUS
Web Reader Tool
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from tools.base_tool import BaseTool


class WebReaderTool(BaseTool):

    name = "web_reader"

    description = "Lee el texto de una página web."

    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL"
            }
        },
        "required": [
            "url"
        ]
    }

    def execute(
        self,
        url: str,
    ):

        r = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "ARUS"
            },
        )

        soup = BeautifulSoup(
            r.text,
            "html.parser",
        )

        return soup.get_text(
            separator="\n",
            strip=True,
        )
