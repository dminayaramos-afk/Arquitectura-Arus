"""
ARUS
Replace Text Tool

Fase 14: no tenía ninguna restricción -- podía modificar cualquier
archivo del sistema al que ARUS tuviera permisos de escritura. Se
añade PathGuard (área de trabajo) y auditoría real.
"""

from pathlib import Path

from tools.base_tool import BaseTool
from security.path_guard import PathGuard
from security.audit_logger import AuditLogger


class ReplaceTextTool(BaseTool):

    name = "replace_text"

    description = "Reemplaza texto dentro de un archivo del área de trabajo de ARUS."

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Ruta del archivo"
            },
            "old": {
                "type": "string",
                "description": "Texto a reemplazar"
            },
            "new": {
                "type": "string",
                "description": "Nuevo texto"
            }
        },
        "required": [
            "path",
            "old",
            "new"
        ]
    }

    def __init__(self):

        self.guard = PathGuard()
        self.audit = AuditLogger()

    def execute(
        self,
        path: str,
        old: str,
        new: str,
    ):

        permitido, motivo = self.guard.validate(path)

        if not permitido:
            self.audit.log(tool="replace_text", arguments={"path": path}, result=motivo)
            return f"ERROR: {motivo}"

        file = Path(path)

        if not file.exists():
            resultado = "ERROR: Archivo no encontrado."
            self.audit.log(tool="replace_text", arguments={"path": path}, result=resultado)
            return resultado

        text = file.read_text(
            encoding="utf-8",
        )

        if old not in text:
            resultado = "ERROR: Texto no encontrado."
            self.audit.log(tool="replace_text", arguments={"path": path}, result=resultado)
            return resultado

        text = text.replace(
            old,
            new,
        )

        file.write_text(
            text,
            encoding="utf-8",
        )

        resultado = "Texto reemplazado correctamente."

        self.audit.log(tool="replace_text", arguments={"path": path}, result=resultado)

        return resultado
