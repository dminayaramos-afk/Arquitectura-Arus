"""
ARUS
Memory Repository

Almacén clave-valor genérico, con namespace, para los distintos tipos
de memoria de la Fase 5 (Long-Term, Semantic, Preferences, Task).

Una sola tabla nueva en tu misma base de datos (arus.db) en lugar de
crear una tabla por tipo de memoria — evita duplicar esquema y
mantiene todo consultable desde un único sitio.
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from database.repository import Repository


class MemoryRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_entries(

            namespace TEXT NOT NULL,

            key TEXT NOT NULL,

            value TEXT,

            tags TEXT,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (namespace, key)
        )
        """)

        self.database.commit()

    def set(self, namespace: str, key: str, value: Any, tags: Optional[list[str]] = None):

        self.cursor.execute(
            """
            INSERT INTO memory_entries(namespace, key, value, tags, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(namespace, key) DO UPDATE SET
                value = excluded.value,
                tags = excluded.tags,
                updated_at = CURRENT_TIMESTAMP
            """,
            (namespace, key, json.dumps(value), json.dumps(tags or [])),
        )

        self.database.commit()

    def get(self, namespace: str, key: str) -> Optional[Any]:

        self.cursor.execute(
            "SELECT value FROM memory_entries WHERE namespace = ? AND key = ?",
            (namespace, key),
        )

        row = self.cursor.fetchone()

        if not row:
            return None

        return json.loads(row["value"])

    def delete(self, namespace: str, key: str):

        self.cursor.execute(
            "DELETE FROM memory_entries WHERE namespace = ? AND key = ?",
            (namespace, key),
        )

        self.database.commit()

    def all(self, namespace: str) -> dict[str, Any]:

        self.cursor.execute(
            "SELECT key, value FROM memory_entries WHERE namespace = ?",
            (namespace,),
        )

        return {row["key"]: json.loads(row["value"]) for row in self.cursor.fetchall()}

    def search(self, namespace: str, query: str) -> list[dict]:
        """
        Búsqueda simple por coincidencia de texto en key/value/tags.
        No es RAG (eso es Fase 8) — solo permite localizar entradas
        por palabra clave sin tener que traerlas todas.
        """

        like = f"%{query}%"

        self.cursor.execute(
            """
            SELECT key, value, tags FROM memory_entries
            WHERE namespace = ? AND (key LIKE ? OR value LIKE ? OR tags LIKE ?)
            ORDER BY updated_at DESC
            """,
            (namespace, like, like, like),
        )

        return [
            {"key": row["key"], "value": json.loads(row["value"]), "tags": json.loads(row["tags"] or "[]")}
            for row in self.cursor.fetchall()
        ]
