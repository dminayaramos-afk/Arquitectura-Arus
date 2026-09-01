"""
ARUS
File Writer Tool

Fase 14: no tenía ninguna restricción -- podía escribir en cualquier
ruta absoluta del sistema que le pidiera el modelo. Se añade
PathGuard (área de trabajo) y auditoría real.
"""

from __future__ import annotations

from pathlib import Path

from tools.base_tool import BaseTool
from security.path_guard import PathGuard
from security.audit_logger import AuditLogger


class FileWriterTool(BaseTool):

    name = "file_writer"

    description = "Escribe texto en un archivo dentro del área de trabajo de ARUS."

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Ruta del archivo"
            },
            "content": {
                "type": "string",
                "description": "Contenido a escribir"
            }
        },
        "required": [
            "path",
            "content"
        ]
    }

    def __init__(self):

        self.guard = PathGuard()
        self.audit = AuditLogger()

    def execute(
        self,
        path: str,
        content: str,
    ):

        permitido, motivo = self.guard.validate(path)

        if not permitido:
            self.audit.log(tool="file_writer", arguments={"path": path}, result=motivo)
            return f"ERROR: {motivo}"

        file = Path(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.write_text(
            content,
            encoding="utf-8",
        )

        resultado = f"Archivo '{path}' escrito correctamente."

        self.audit.log(tool="file_writer", arguments={"path": path, "bytes": len(content)}, result=resultado)

        return resultado
