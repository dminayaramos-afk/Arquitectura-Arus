"""
ARUS
Document Parser (Fase 8)

Lee el contenido de texto de un archivo de forma segura. Alcance
deliberado: texto plano, Markdown y código fuente (lo que se puede
decodificar como UTF-8). PDF y DOCX necesitan librerías adicionales
(pypdf / python-docx) que no están confirmadas en este proyecto —
quedan fuera de esta fase en vez de fingir soporte.
"""

from __future__ import annotations

from pathlib import Path

# Extensiones que se tratan como texto. Cualquier otra extensión se
# rechaza explícitamente en vez de intentar decodificarla a ciegas.
EXTENSIONES_TEXTO = {
    ".txt", ".md", ".rst",
    ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".sh", ".bat", ".ps1",
    ".html", ".css", ".xml", ".csv",
}

# No indexar archivos enormes en un equipo con recursos limitados
# (punto 89: "RAG pesado" es condicional/no recomendado en hardware
# limitado; aquí se traduce en un límite de tamaño razonable).
LIMITE_BYTES = 2 * 1024 * 1024  # 2 MB


class DocumentParser:

    def puede_leer(self, path: Path) -> bool:

        return path.suffix.lower() in EXTENSIONES_TEXTO

    def leer(self, path: Path) -> str:

        if not path.exists():
            raise FileNotFoundError(f"No existe: {path}")

        if not path.is_file():
            raise ValueError(f"No es un archivo: {path}")

        if not self.puede_leer(path):
            raise ValueError(
                f"Extensión no soportada para RAG: {path.suffix} "
                f"(solo texto/código, ver rag.document_parser.EXTENSIONES_TEXTO)"
            )

        if path.stat().st_size > LIMITE_BYTES:
            raise ValueError(
                f"Archivo demasiado grande para indexar ({path.stat().st_size} bytes, "
                f"límite {LIMITE_BYTES})."
            )

        return path.read_text(encoding="utf-8", errors="ignore")
