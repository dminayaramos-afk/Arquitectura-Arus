"""
ARUS
Router principal.

Decide qué módulo debe procesar el mensaje.
"""

from __future__ import annotations


class Router:

    def route(self, message: str) -> str:

        message = message.lower()

        if "hola" in message:
            return "chat"

        if "adiós" in message:
            return "chat"

        if "linux" in message:
            return "knowledge"

        if "python" in message:
            return "coding"

        return "chat"
