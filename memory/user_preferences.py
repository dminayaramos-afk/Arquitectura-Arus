"""
ARUS
User Preferences

Preferencias explícitas del usuario (punto 6 del prompt maestro).
Ejemplo: idioma preferido, formato de respuesta, unidades, etc.
Separado de Long Memory porque son datos de naturaleza distinta
(configuración vs. conocimiento/hechos), aunque comparten el mismo
mecanismo de persistencia (MemoryRepository).
"""

from __future__ import annotations

from database.database import Database
from database.memory_repository import MemoryRepository

_NAMESPACE = "preferences"


class UserPreferences:

    def __init__(self, database=None):

        self.database = database or Database()

        self.repo = MemoryRepository(self.database)

        self.repo.create_table()

    def set(self, key: str, value):

        self.repo.set(_NAMESPACE, key, value)

    def get(self, key: str, default=None):

        value = self.repo.get(_NAMESPACE, key)

        return value if value is not None else default

    def unset(self, key: str):

        self.repo.delete(_NAMESPACE, key)

    def all(self):

        return self.repo.all(_NAMESPACE)
