"""
ARUS
Proveedor genérico "compatible con OpenAI"

ARUS es un cuerpo pensado para conectarse a cualquier IA, no solo a
Ollama. La mayoría de motores de inferencia local que NO son Ollama
(LM Studio, llama.cpp `server`, koboldcpp, text-generation-webui con su
extensión "openai", vLLM, LocalAI, etc.) exponen el mismo formato de API
que OpenAI: un endpoint HTTP `POST /chat/completions` con un cuerpo
`{"model": ..., "messages": [...]}`. Implementando ese único formato,
ARUS puede hablar con cualquiera de ellos sin necesitar un proveedor
distinto para cada programa.

No se implementa la librería oficial `openai` (no está entre las
dependencias del proyecto y sería una dependencia pesada para algo tan
simple); basta con `requests`, que ya usa el resto del proyecto.
"""

from __future__ import annotations

import requests

from ai.providers.base_provider import BaseProvider


class OpenAICompatibleProvider(BaseProvider):
    """Habla con cualquier servidor local que exponga la API estilo OpenAI.

    Sirve, entre otros, para: LM Studio, llama.cpp `server`, koboldcpp,
    text-generation-webui (extensión openai), vLLM, LocalAI, y también
    servicios remotos reales de OpenAI si se les da la clave/host
    correctos (aunque el enfoque de ARUS es priorizar lo local).
    """

    name = "openai_compatible"

    def __init__(
        self,
        host: str = "http://127.0.0.1:1234/v1",
        model: str = "local-model",
        api_key: str | None = None,
        system_prompt: str | None = None,
        timeout: int = 60,
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.system_prompt = system_prompt or (
            "Eres ARUS, un asistente virtual. Responde de forma breve, "
            "clara y directa."
        )
        self.timeout = timeout

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def generate(self, prompt: str, history=None) -> str:
        messages = []

        if not history or history[0].get("role") != "system":
            messages.append({"role": "system", "content": self.system_prompt})

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": str(prompt)})

        try:
            response = requests.post(
                f"{self.host}/chat/completions",
                json={"model": self.model, "messages": messages},
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            return (
                f"No se pudo conectar con el servidor de IA en {self.host}. "
                "¿Está encendido? (LM Studio, llama.cpp server, koboldcpp, "
                "text-generation-webui...)"
            )
        except requests.exceptions.Timeout:
            return "El servidor de IA tardó demasiado en responder (timeout)."
        except Exception as e:
            return f"Error hablando con el proveedor de IA en {self.host}: {e}"
