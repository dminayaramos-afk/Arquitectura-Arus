"""
ARUS
Embeddings (Fase 8)

Vector por "hashing trick": cada palabra se manda a una posición fija
de un vector de tamaño fijo (via hash estable) y se cuenta su
frecuencia; el vector se normaliza (L2). No requiere descargar ningún
modelo ni librerías de ML — funciona sin internet y en hardware
limitado (ver decisión de diseño en rag/__init__.py).

No es tan preciso como un embedding semántico real (un modelo no
distinguirá sinónimos), pero es determinista, rápido, y suficiente
para la búsqueda por similitud de esta fase. Si en el futuro hay
GPU/modelo de embeddings disponible (Fase de hardware/CapabilityManager),
esta clase se puede sustituir sin tocar VectorStore ni Retriever.
"""

from __future__ import annotations

import hashlib
import math
import re

DIMENSIONES = 256

_PALABRA = re.compile(r"[a-záéíóúüñ0-9]+", re.IGNORECASE)


class Embeddings:

    def __init__(self, dimensiones: int = DIMENSIONES):

        self.dimensiones = dimensiones

    def _tokenizar(self, texto: str) -> list[str]:

        return _PALABRA.findall(texto.lower())

    def vectorizar(self, texto: str) -> list[float]:

        vector = [0.0] * self.dimensiones

        for palabra in self._tokenizar(texto):

            indice = int(
                hashlib.md5(palabra.encode("utf-8")).hexdigest(), 16
            ) % self.dimensiones

            vector[indice] += 1.0

        norma = math.sqrt(sum(v * v for v in vector))

        if norma > 0:
            vector = [v / norma for v in vector]

        return vector

    @staticmethod
    def similitud_coseno(a: list[float], b: list[float]) -> float:

        return sum(x * y for x, y in zip(a, b))
