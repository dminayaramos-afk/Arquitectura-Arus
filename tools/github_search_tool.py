"""
ARUS
GitHub Search Tool
"""

from __future__ import annotations

import requests

from tools.base_tool import BaseTool


class GithubSearchTool(BaseTool):

    name = "github_search"

    description = "Busca repositorios públicos en GitHub."

    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Búsqueda"
            }
        },
        "required": [
            "query"
        ]
    }

    def execute(
        self,
        query: str,
    ):

        url = (
            "https://api.github.com/search/repositories"
            f"?q={query}&per_page=5"
        )

        r = requests.get(
            url,
            timeout=20,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "ARUS"
            }
        )

        data = r.json()

        if "items" not in data:
            return str(data)

        text = ""

        for repo in data["items"]:

            text += (
                f"{repo['full_name']}\n"
                f"{repo['html_url']}\n"
                f"⭐ {repo['stargazers_count']}\n"
                f"{repo['description']}\n\n"
            )

        return text
