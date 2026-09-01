"""
ARUS
Proveedor "none"

Se usa cuando el usuario todavía no ha conectado ninguna IA (ver
config/settings.json -> "ai_provider"). En vez de intentar hablar con
Ollama a ciegas y fallar con un error críptico, ARUS responde con un
mensaje claro que explica cómo conectar una.
"""

from __future__ import annotations

from ai.providers.base_provider import BaseProvider


class NoneProvider(BaseProvider):

    name = "none"

    def generate(self, prompt: str, history=None) -> str:
        return (
            "Todavía no tengo ninguna IA conectada. Configura al menos un "
            "proveedor en config/settings.json (clave \"ai_providers\") y "
            "marca cuál usar por defecto en \"ai_provider\"."
        )
