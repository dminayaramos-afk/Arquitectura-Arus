"""
ARUS
Semantic Memory

Conocimiento recuperable relacionado con documentos/proyectos
(punto 6 del prompt maestro). Búsqueda simple por palabra clave
sobre lo que se le enseña a ARUS.

Esto NO es RAG (embeddings/vector store) — eso es la Fase 8. Es la
base mínima sobre la que la Fase 8 podrá construir: cuando exista un
Vector Store real, podrá sustituir este `search()` por una búsqueda
semántica de verdad sin cambiar la API que usa MemoryManager.
"""

from __future__ import annotations

from database.database import Database
from database.memory_repository import MemoryRepository

_NAMESPACE = "semantic"


class SemanticMemory:

    def __init__(self, database=None):

        self.database = database or Database()

        self.repo = MemoryRepository(self.database)

        self.repo.create_table()

    def add(self, key: str, content: str, tags: list[str] | None = None):

        self.repo.set(_NAMESPACE, key, content, tags=tags)

    def get(self, key: str):

        return self.repo.get(_NAMESPACE, key)

    def forget(self, key: str):

        self.repo.delete(_NAMESPACE, key)

    def all(self):

        return self.repo.all(_NAMESPACE)

    def search(self, query: str, limit: int = 5) -> list[dict]:

        results = self.repo.search(_NAMESPACE, query)

        return results[:limit]
