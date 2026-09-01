"""
ARUS
Shell Tool

Fase 14 -- hallazgo más grave de toda la auditoría de seguridad: esta
herramienta se describía a sí misma como "Ejecuta comandos en la
terminal de forma segura", pero `execute()` hacía
`subprocess.run(command, shell=True, ...)` con el comando tal cual
venía del modelo, SIN ninguna comprobación. `security/shell_guard.py`
existía con una lista de comandos bloqueados y una lista de comandos
permitidos, pensado exactamente para esto -- pero nada lo llamaba
(auditado antes de tocar nada, igual que Planner/TaskManager en la
Fase 6 o AuditLogger en la Fase 9). Como esta tool ya está expuesta al
modelo por function-calling desde la Fase 6, esto era un hueco de
seguridad real y explotable, no solo teórico.

No se le añade un parámetro de "confirmación" que el modelo pudiera
rellenar él mismo (mismo criterio que con `git commit`, Fase 9). En
su lugar, ShellGuard actúa como límite automático y objetivo: solo se
permiten comandos de una lista cerrada, y ninguno que contenga un
patrón peligroso conocido.
"""

import subprocess
from tools.base_tool import BaseTool
from security.shell_guard import ShellGuard
from security.audit_logger import AuditLogger


class ShellTool(BaseTool):
    name = "shell"
    description = "Ejecuta comandos de una lista permitida en la terminal (con lista negra de patrones peligrosos)."
    parameters = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Comando de terminal a ejecutar"}
        },
        "required": ["command"]
    }

    def __init__(self):
        self.guard = ShellGuard()
        self.audit = AuditLogger()

    def execute(self, command: str):

        if not self.guard.allowed(command):
            resultado = (
                "ERROR: comando bloqueado por seguridad (no está en la lista "
                "de comandos permitidos, o contiene un patrón peligroso)."
            )
            self.audit.log(tool="shell", arguments={"command": command}, result=resultado)
            return resultado

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                resultado = result.stdout if result.stdout else "Comando ejecutado con éxito (sin salida)."
            else:
                resultado = f"ERROR: {result.stderr}"
        except Exception as e:
            resultado = f"ERROR: {str(e)}"

        self.audit.log(tool="shell", arguments={"command": command}, result=resultado[:200])
        return resultado
