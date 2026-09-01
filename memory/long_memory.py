"""
ARUS
Long Memory

Antes: un diccionario en RAM (self.knowledge = {}) que se perdía por
completo al cerrar ARUS — contradecía su propio propósito
("información que debe sobrevivir a futuras sesiones", punto 6 del
prompt maestro). Ahora persiste en la misma base de datos (arus.db,
tabla memory_entries, namespace "long") a través de MemoryRepository,
sin crear una base de datos nueva.

La API pública (remember/recall/all) no cambia, así que nada que ya
la use (brain.think()) necesita modificarse.
"""

from __future__ import annotations

from database.database import Database
from database.memory_repository import MemoryRepository

_NAMESPACE = "long"


class LongMemory:

    def __init__(self, database=None):

        self.database = database or Database()

        self.repo = MemoryRepository(self.database)

        self.repo.create_table()

    def remember(self, key: str, value):

        self.repo.set(_NAMESPACE, key, value)

    def recall(self, key: str):

        return self.repo.get(_NAMESPACE, key)

    def forget(self, key: str):

        self.repo.delete(_NAMESPACE, key)

    def all(self):

        return self.repo.all(_NAMESPACE)

    def search(self, query: str):

        return self.repo.search(_NAMESPACE, query)
