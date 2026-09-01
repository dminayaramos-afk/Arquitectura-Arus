"""
ARUS
Git Tool (Fase 9, punto 21 del prompt maestro)

Alcance deliberado: SOLO LECTURA (status, diff, log, ramas, README).

Por qué no hay "commit" ni "push" funcionales aquí: el prompt maestro
pide "crear commits bajo autorización" y "nunca hacer push... sin
autorización" (puntos 21 y 40). El problema real es que estas
herramientas se las ofrecemos al modelo por function-calling — es
decir, quien "pide" ejecutar la herramienta es el propio modelo, no
un humano pulsando un botón. Si expusiera un parámetro como
`confirmed: bool` en el esquema de la tool, nada impediría que el
modelo se auto-confirmara sus propios commits, lo cual no es
autorización real, es fingirla. Como la interfaz (intocable en este
proyecto) todavía no tiene un mecanismo para pedirle confirmación de
verdad a un humano y bloquear hasta obtenerla, escribir commits reales
aquí sería crear justo el agujero de seguridad que el prompt maestro
pide evitar. Se deja sin implementar, con una acción `commit` que
explica esto en vez de fingir que funciona.

Se usa `AuditLogger` (existía en el proyecto pero no lo llamaba nadie
todavía) para dejar constancia de cada consulta Git — punto 41 del
prompt maestro.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from tools.base_tool import BaseTool
from security.audit_logger import AuditLogger

ACCIONES_SOLO_LECTURA = {
    "status", "diff", "log", "branches", "current_branch", "readme",
}


class GitTool(BaseTool):

    name = "git"

    description = (
        "Consulta un repositorio Git local: status, diff, log, ramas, "
        "rama actual o el README. Solo lectura -- no crea commits ni "
        "hace push."
    )

    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": (
                    "status | diff | log | branches | current_branch | "
                    "readme | commit"
                ),
            },
            "repo_path": {
                "type": "string",
                "description": "Ruta del repositorio (por defecto, el directorio actual).",
            },
            "limit": {
                "type": "integer",
                "description": "Para 'log': número de commits a mostrar (por defecto 10).",
            },
        },
        "required": ["action"],
    }

    def __init__(self):

        self._audit = AuditLogger()

    def execute(self, action: str, repo_path: str = ".", limit: int = 10):

        resultado = self._ejecutar(action, repo_path, limit)

        self._audit.log(
            tool="git",
            arguments={"action": action, "repo_path": repo_path, "limit": limit},
            result=resultado,
        )

        return resultado

    def _ejecutar(self, action: str, repo_path: str, limit: int):

        if action == "commit":
            return (
                "No implementado: crear commits requiere autorización humana "
                "real, y todavía no existe un mecanismo en la interfaz para "
                "pedirla y esperarla (ver docstring de git_tool.py). No se "
                "va a fingir esa confirmación."
            )

        if action not in ACCIONES_SOLO_LECTURA:
            return f"Acción no soportada: {action}"

        ruta = Path(repo_path)

        if not ruta.exists():
            return f"ERROR: la ruta no existe: {repo_path}"

        if not self._es_repo_git(ruta):
            return f"ERROR: '{repo_path}' no es un repositorio Git."

        if action == "readme":
            return self._leer_readme(ruta)

        comando = {
            "status": ["git", "-C", str(ruta), "status", "--short", "--branch"],
            "diff": ["git", "-C", str(ruta), "diff"],
            "log": ["git", "-C", str(ruta), "log", f"-n{max(1, int(limit))}", "--oneline"],
            "branches": ["git", "-C", str(ruta), "branch", "--all"],
            "current_branch": ["git", "-C", str(ruta), "rev-parse", "--abbrev-ref", "HEAD"],
        }[action]

        return self._correr(comando)

    def _es_repo_git(self, ruta: Path) -> bool:

        resultado = subprocess.run(
            ["git", "-C", str(ruta), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=15,
        )

        return resultado.returncode == 0 and resultado.stdout.strip() == "true"

    def _correr(self, comando: list) -> str:

        try:

            resultado = subprocess.run(
                comando, capture_output=True, text=True, timeout=30,
            )

            if resultado.returncode != 0:
                return f"ERROR: {resultado.stderr.strip()}"

            return resultado.stdout.strip() or "(sin salida)"

        except Exception as e:

            return f"ERROR: {e}"

    def _leer_readme(self, ruta: Path) -> str:

        for nombre in ("README.md", "README.rst", "README.txt", "README"):

            candidato = ruta / nombre

            if candidato.exists():

                try:
                    return candidato.read_text(encoding="utf-8", errors="ignore")
                except Exception as e:
                    return f"ERROR leyendo {nombre}: {e}"

        return "No se encontró README en el repositorio."
