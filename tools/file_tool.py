"""
ARUS
File Tool

Fase 14: la clase `Sandbox` de aquí tenía un `validate(path)` que
SIEMPRE devolvía `True` -- un sandbox falso, sin ninguna comprobación
real (auditado y corregido, ver security/path_guard.py). Sustituido
por PathGuard, que sí restringe de verdad al área de trabajo. También
se añade auditoría real (antes esta tool no dejaba ningún rastro de
qué archivos tocaba).
"""

from pathlib import Path
from tools.base_tool import BaseTool
from security.path_guard import PathGuard
from security.audit_logger import AuditLogger


class FileTool(BaseTool):
    name = "file"
    description = "Lee o escribe contenido de archivos dentro del área de trabajo de ARUS."
    parameters = {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "Acción: read o write"},
            "path": {"type": "string", "description": "Ruta del archivo"},
            "content": {"type": "string", "description": "Contenido para escribir (opcional)"}
        },
        "required": ["action", "path"]
    }

    def __init__(self):
        self.guard = PathGuard()
        self.audit = AuditLogger()

    def execute(self, action: str, path: str, content: str = ""):
        permitido, motivo = self.guard.validate(path)

        if not permitido:
            self.audit.log(tool="file", arguments={"action": action, "path": path}, result=motivo)
            return f"ERROR: {motivo}"

        target = Path(path)
        if action == "read":
            if not target.exists():
                resultado = "ERROR: El archivo no existe."
            else:
                try:
                    resultado = target.read_text(encoding="utf-8")
                except Exception as e:
                    resultado = str(e)
        elif action == "write":
            try:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
                resultado = "OK"
            except Exception as e:
                resultado = str(e)
        else:
            resultado = "ERROR: Acción desconocida."

        self.audit.log(tool="file", arguments={"action": action, "path": path}, result=resultado[:200])
        return resultado
