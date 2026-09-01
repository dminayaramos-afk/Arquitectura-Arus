"""
ARUS
Vector Store (Fase 8)

Guarda los vectores en SQLite (vía RagChunkRepository) y busca por
similitud de coseno en Python. Para el volumen de documentos que
puede manejar un equipo con recursos limitados (punto 89 del prompt
maestro) esto es suficiente sin necesitar una base de datos vectorial
dedicada (Faiss, Chroma, etc.) — si el proyecto crece mucho y hay
hardware disponible, se podrá sustituir el backend sin cambiar la API
de Retriever/RAGManager.
"""

from __future__ import annotations

from database.database import Database
from database.rag_chunk_repository import RagChunkRepository
from rag.embeddings import Embeddings


class VectorStore:

    def __init__(self, database: Database = None):

        self.database = database or Database()

        self.repo = RagChunkRepository(self.database)

        self.repo.create_table()

        self.embeddings = Embeddings()

    def index(self, project: str, source: str, chunks: list[str]):
        """Reemplaza los fragmentos anteriores de `source` por los nuevos."""

        self.repo.delete_source(source)

        for i, chunk in enumerate(chunks):

            vector = self.embeddings.vectorizar(chunk)

            self.repo.add(project, source, i, chunk, vector)

    def search(self, query: str, project: str = None, top_k: int = 5) -> list[dict]:

        vector_query = self.embeddings.vectorizar(query)

        candidatos = self.repo.all(project=project)

        puntuados = []

        for candidato in candidatos:

            score = self.embeddings.similitud_coseno(vector_query, candidato["vector"])

            puntuados.append((score, candidato))

        puntuados.sort(key=lambda par: par[0], reverse=True)

        resultados = []

        for score, candidato in puntuados[:top_k]:

            resultados.append({
                "source": candidato["source"],
                "chunk_index": candidato["chunk_index"],
                "content": candidato["content"],
                "score": score,
            })

        return resultados

    def sources(self, project: str = None) -> list[str]:

        return self.repo.sources(project=project)

    def count(self, project: str = None) -> int:

        return self.repo.count(project=project)
