"""
ARUS
Vision Provider (Fase 12)

Ollama soporta modelos multimodales (p.ej. llava, qwen2.5vl) pasando
`images` en el mensaje. El modelo configurado hoy en
`ai/providers/local_provider.py` es `qwen2.5:3b` -- que NO es
multimodal. Este provider comprueba de verdad si el modelo de visión
indicado existe en Ollama antes de intentar usarlo; si no, lo dice
honestamente en vez de fingir un análisis.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class VisionProvider(ABC):

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def analyze(self, image_base64: str, prompt: str) -> str:
        ...


class OllamaVisionProvider(VisionProvider):

    def __init__(self, model: str = "llava", host: str = "http://127.0.0.1:11434"):

        self.model = model
        self.host = host

    def _cliente(self):

        import ollama

        return ollama.Client(host=self.host)

    def is_available(self) -> bool:
        """
        Comprueba de verdad que Ollama está corriendo Y que el
        modelo de visión indicado está instalado -- no asume nada.
        """

        try:

            cliente = self._cliente()

            modelos = cliente.list()

            nombres = [m.get("name", m.get("model", "")) for m in modelos.get("models", [])]

            return any(self.model in nombre for nombre in nombres)

        except Exception:

            return False

    def analyze(self, image_base64: str, prompt: str) -> str:

        if not self.is_available():
            return (
                f"Visión no disponible: el modelo '{self.model}' no está "
                "instalado en Ollama (o Ollama no está accesible). Instálalo "
                f"con 'ollama pull {self.model}' para activar el análisis "
                "de imágenes."
            )

        cliente = self._cliente()

        respuesta = cliente.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64],
                }
            ],
        )

        return respuesta.message.content
