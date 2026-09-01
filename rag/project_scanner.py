"""
ARUS
Project Scanner (Fase 8 / punto 24 y 55 del prompt maestro)

Recorre un proyecto para indexarlo con RAG. Alcance deliberado: listar
y leer los archivos de texto/código del proyecto. NO analiza Git ni
dependencias de forma especial (eso es Fase 9 y ya se puede consultar
como texto normal, p.ej. requirements.txt queda indexado igual que
cualquier otro archivo) — evita fingir un análisis que no existe
todavía.
"""

from __future__ import annotations

from pathlib import Path

from rag.document_parser import DocumentParser

# Carpetas que nunca tiene sentido indexar (entornos virtuales,
# control de versiones, caches, dependencias de terceros...).
CARPETAS_IGNORADAS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    "_archivo_backups", "dist", "build", ".idea", ".vscode",
}

# Un límite de archivos por defecto para no intentar indexar un
# proyecto entero de golpe en un equipo con recursos limitados
# (punto 89). Se puede subir explícitamente si el usuario lo pide.
LIMITE_ARCHIVOS_POR_DEFECTO = 500


class ProjectScanner:

    def __init__(self, parser: DocumentParser = None):

        self.parser = parser or DocumentParser()

    def scan(self, root: str, limite_archivos: int = LIMITE_ARCHIVOS_POR_DEFECTO) -> list[Path]:
        """Devuelve la lista de archivos indexables del proyecto (sin leerlos aún)."""

        raiz = Path(root)

        if not raiz.exists() or not raiz.is_dir():
            raise ValueError(f"No es un directorio válido: {root}")

        encontrados = []

        for path in raiz.rglob("*"):

            if not path.is_file():
                continue

            if any(parte in CARPETAS_IGNORADAS for parte in path.parts):
                continue

            if not self.parser.puede_leer(path):
                continue

            encontrados.append(path)

            if len(encontrados) >= limite_archivos:
                break

        return encontrados
