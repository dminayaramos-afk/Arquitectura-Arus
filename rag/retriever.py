"""
ARUS
Retriever (Fase 8)

Punto único por el que Brain (cuando se conecte) pediría contexto
relevante, sin tener que saber nada de chunking/embeddings/SQLite.
"""

from __future__ import annotations

from rag.vector_store import VectorStore


class Retriever:

    def __init__(self, vector_store: VectorStore = None):

        self.vector_store = vector_store or VectorStore()

    def retrieve(self, query: str, project: str = None, top_k: int = 5) -> list[dict]:

        return self.vector_store.search(query, project=project, top_k=top_k)

    def retrieve_as_text(self, query: str, project: str = None, top_k: int = 5) -> str:
        """
        Da formato de texto a los fragmentos recuperados, listo para
        insertarse en un prompt sin meter el documento entero
        (punto 23 del prompt maestro).
        """

        resultados = self.retrieve(query, project=project, top_k=top_k)

        if not resultados:
            return ""

        partes = []

        for r in resultados:
            partes.append(f"[{r['source']} #{r['chunk_index']}]\n{r['content']}")

        return "\n\n".join(partes)
