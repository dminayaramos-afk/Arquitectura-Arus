"""
ARUS
Web Tool

Fase 16: `execute()` devolvía SIEMPRE "Contenido simulado para la URL:
{url}", sin hacer ninguna petición real -- se detecto al construir la
evaluacion automatica (no tenia sentido "evaluar" una capacidad web
que era pura ficcion). Ahora hace una petición HTTP real (GET),
pensada para APIs/JSON/contenido crudo. Para extraer texto legible de
una pagina HTML, usa `web_reader` (esa si era real desde antes).
"""

from __future__ import annotations

import requests

from tools.base_tool import BaseTool

LIMITE_BYTES = 500_000


class WebTool(BaseTool):

    name = "web"

    description = "Realiza una petición HTTP GET real a una URL y devuelve el contenido (útil para APIs)."

    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL a consultar"}
        },
        "required": ["url"]
    }

    def execute(self, url: str):

        if not url.startswith(("http://", "https://")):
            return "ERROR: la URL debe empezar por http:// o https://"

        try:

            respuesta = requests.get(
                url,
                timeout=20,
                headers={"User-Agent": "ARUS"},
            )

            contenido = respuesta.text[:LIMITE_BYTES]

            return f"[HTTP {respuesta.status_code}]\n{contenido}"

        except requests.exceptions.RequestException as e:

            return f"ERROR: no se pudo acceder a la URL ({e})"
