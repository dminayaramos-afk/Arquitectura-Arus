"""
ARUS
RAG Chunk Repository (Fase 8)

Persistencia de los fragmentos indexados (texto + vector + metadatos),
siguiendo el mismo patrón Repository/Database que el resto del
proyecto (ver database/conversation_session_repository.py,
database/memory_repository.py).
"""

from __future__ import annotations

import json

from database.repository import Repository


class RagChunkRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS rag_chunks(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            project TEXT,

            source TEXT,

            chunk_index INTEGER,

            content TEXT,

            vector TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.database.commit()

    def add(self, project: str, source: str, chunk_index: int, content: str, vector: list[float]):

        self.cursor.execute(
            "INSERT INTO rag_chunks(project, source, chunk_index, content, vector) "
            "VALUES (?, ?, ?, ?, ?)",
            (project or "", source, chunk_index, content, json.dumps(vector)),
        )

        self.database.commit()

    def delete_source(self, source: str):
        """Antes de reindexar un archivo, borra sus fragmentos anteriores."""

        self.cursor.execute(
            "DELETE FROM rag_chunks WHERE source = ?",
            (source,),
        )

        self.database.commit()

    def all(self, project: str = None) -> list[dict]:

        if project:
            self.cursor.execute(
                "SELECT * FROM rag_chunks WHERE project = ?",
                (project,),
            )
        else:
            self.cursor.execute("SELECT * FROM rag_chunks")

        filas = []

        for row in self.cursor.fetchall():

            fila = dict(row)
            fila["vector"] = json.loads(fila["vector"])
            filas.append(fila)

        return filas

    def sources(self, project: str = None) -> list[str]:

        if project:
            self.cursor.execute(
                "SELECT DISTINCT source FROM rag_chunks WHERE project = ?",
                (project,),
            )
        else:
            self.cursor.execute("SELECT DISTINCT source FROM rag_chunks")

        return [row["source"] for row in self.cursor.fetchall()]

    def count(self, project: str = None) -> int:

        if project:
            self.cursor.execute(
                "SELECT COUNT(*) as n FROM rag_chunks WHERE project = ?",
                (project,),
            )
        else:
            self.cursor.execute("SELECT COUNT(*) as n FROM rag_chunks")

        return self.cursor.fetchone()["n"]
