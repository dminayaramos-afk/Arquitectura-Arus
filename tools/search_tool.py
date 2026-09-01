"""
ARUS
Search Tool

Fase 16: `execute()` devolvía SIEMPRE "Resultados para la búsqueda:
{query}", sin buscar nada de verdad. Sustituido por una búsqueda real
sin necesitar clave de API: el endpoint HTML de DuckDuckGo (no
requiere registro ni token). Si no hay conexión o el servicio no
responde, se dice con claridad -- no se inventan resultados.
"""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from tools.base_tool import BaseTool

MAX_RESULTADOS = 5


class SearchTool(BaseTool):

    name = "search"

    description = "Busca información en la web (DuckDuckGo, sin necesitar clave de API) y devuelve los primeros resultados."

    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Consulta de búsqueda"}
        },
        "required": ["query"]
    }

    def execute(self, query: str):

        try:

            respuesta = requests.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query},
                timeout=20,
                headers={"User-Agent": "ARUS"},
            )

            respuesta.raise_for_status()

        except requests.exceptions.RequestException as e:

            return f"ERROR: no se pudo realizar la búsqueda ({e})"

        soup = BeautifulSoup(respuesta.text, "html.parser")

        resultados = []

        for enlace in soup.select("a.result__a")[:MAX_RESULTADOS]:

            titulo = enlace.get_text(strip=True)
            url = enlace.get("href", "")

            if titulo:
                resultados.append(f"- {titulo}\n  {url}")

        if not resultados:
            return f"Sin resultados para: {query}"

        return "\n".join(resultados)
