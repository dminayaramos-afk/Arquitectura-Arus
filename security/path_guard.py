"""
ARUS
Path Guard (Fase 14, punto 39-40 del prompt maestro)

Hallazgo grave que motiva este archivo: `tools/file_tool.py` tenía
una clase `Sandbox` cuyo `validate(path)` SIEMPRE devolvía `True`,
sin comprobar nada -- daba la sensación de que había protección
cuando no había ninguna. Eso es peor que no tener sandbox: genera
falsa confianza. Se sustituye por una comprobación real.

Restringe operaciones de archivo a un directorio base (por defecto,
el directorio de trabajo actual de ARUS), resolviendo `..` y enlaces
simbólicos antes de comparar, para que no sirva escribir
'../../etc/passwd' ni similares.

No pide confirmación con un parámetro que el modelo pueda rellenar él
mismo (mismo criterio que con `git commit` en la Fase 9: el modelo no
puede autoconfirmarse su propia autorización). En su lugar, es un
límite automático y objetivo: dentro del área de trabajo, permitido;
fuera, denegado siempre, sin excepción configurable desde la
herramienta.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional


class PathGuard:

    def __init__(self, base_dir: Optional[str] = None):

        self.base_dir = Path(base_dir or Path.cwd()).resolve()

    def validate(self, path: str) -> tuple[bool, str]:

        try:
            resuelto = Path(path).resolve()
        except Exception as e:
            return False, f"Ruta inválida: {e}"

        try:
            resuelto.relative_to(self.base_dir)
        except ValueError:
            return False, (
                f"Acceso denegado: '{path}' está fuera del área de trabajo "
                f"permitida ({self.base_dir})."
            )

        return True, ""
