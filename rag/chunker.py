"""
ARUS
Chunker (Fase 8)

Divide texto largo en fragmentos manejables, con solapamiento para no
cortar ideas por la mitad. Trocea por líneas (no por tokens de un
tokenizer real, que añadiría una dependencia pesada innecesaria para
esto).
"""

from __future__ import annotations


class Chunker:

    def __init__(self, max_chars: int = 1200, overlap_chars: int = 150):

        if overlap_chars >= max_chars:
            raise ValueError("overlap_chars debe ser menor que max_chars")

        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def split(self, text: str) -> list[str]:

        text = text.strip()

        if not text:
            return []

        if len(text) <= self.max_chars:
            return [text]

        chunks = []

        inicio = 0

        while inicio < len(text):

            fin = min(inicio + self.max_chars, len(text))

            chunk = text[inicio:fin].strip()

            if chunk:
                chunks.append(chunk)

            if fin >= len(text):
                break

            inicio = fin - self.overlap_chars

        return chunks
