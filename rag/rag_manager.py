"""
ARUS
RAG Manager (Fase 8)

Fachada única del pipeline Documents -> Parser -> Chunking ->
Embeddings -> Vector Store -> Retriever (punto 23), más el escaneo de
proyectos completos (punto 24 / 55).

No se conecta todavía a Brain.think() de forma automática: decidir
CUÁNDO inyectar contexto recuperado en cada respuesta (¿siempre?
¿solo si se detecta cierta intención?) es una decisión de producto que
afecta al flujo ya probado de las Fases 2-7, así que se deja fuera de
esta fase para no arriesgar una regresión. Brain expone `self.rag`
(ver brain/brain.py) listo para que una fase futura, o tú
explícitamente, decida cómo y cuándo usarlo.
"""

from __future__ import annotations

from pathlib import Path

from rag.document_parser import DocumentParser
from rag.chunker import Chunker
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.project_scanner import ProjectScanner


class RAGManager:

    def __init__(
        self,
        vector_store: VectorStore = None,
        chunker: Chunker = None,
        parser: DocumentParser = None,
    ):

        self.parser = parser or DocumentParser()

        self.chunker = chunker or Chunker()

        self.vector_store = vector_store or VectorStore()

        self.retriever = Retriever(self.vector_store)

        self.scanner = ProjectScanner(self.parser)

    def index_file(self, path: str, project: str = None) -> int:
        """Indexa un archivo. Devuelve el número de fragmentos guardados."""

        ruta = Path(path)

        texto = self.parser.leer(ruta)

        chunks = self.chunker.split(texto)

        self.vector_store.index(project, str(ruta), chunks)

        return len(chunks)

    def index_project(self, root: str, project: str = None, limite_archivos: int = None) -> dict:
        """
        "Aprende este proyecto" (punto 55): scan -> analyze(leer) ->
        index -> resumen de lo indexado. El resumen en lenguaje
        natural (no solo cifras) necesitaría el modelo -eso es
        integración con Brain, no esta fase-, así que aquí se
        devuelve un resumen de hechos verificables.
        """

        nombre_proyecto = project or str(Path(root).resolve())

        kwargs = {}
        if limite_archivos is not None:
            kwargs["limite_archivos"] = limite_archivos

        archivos = self.scanner.scan(root, **kwargs)

        indexados = 0
        fragmentos_totales = 0
        omitidos = []

        for archivo in archivos:

            try:
                n = self.index_file(str(archivo), project=nombre_proyecto)
                indexados += 1
                fragmentos_totales += n

            except Exception as e:

                omitidos.append({"archivo": str(archivo), "motivo": str(e)})

        return {
            "project": nombre_proyecto,
            "archivos_encontrados": len(archivos),
            "archivos_indexados": indexados,
            "fragmentos": fragmentos_totales,
            "omitidos": omitidos,
        }

    def query(self, text: str, project: str = None, top_k: int = 5) -> list[dict]:

        return self.retriever.retrieve(text, project=project, top_k=top_k)

    def query_as_text(self, text: str, project: str = None, top_k: int = 5) -> str:

        return self.retriever.retrieve_as_text(text, project=project, top_k=top_k)

    def status(self, project: str = None) -> dict:

        return {
            "project": project,
            "fragmentos_indexados": self.vector_store.count(project=project),
            "fuentes": self.vector_store.sources(project=project),
        }
