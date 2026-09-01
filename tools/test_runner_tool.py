"""
ARUS
Test Runner Tool (Fase 10, punto 18: "ejecutar tests", "analizar resultados")

Antes de escribir esto se comprobó (punto 103 del prompt maestro:
"¿es realmente necesaria? comprobar primero si ya está instalada") si
pytest estaba disponible en el proyecto -- no lo está. En vez de
imponer una dependencia nueva, esta herramienta usa pytest SI el
usuario ya lo tiene instalado, y si no, cae a `unittest` (viene con
Python, cero dependencias nuevas). Así funciona tal cual en el
proyecto de Danny hoy mismo, y automáticamente aprovecha pytest si en
algún momento lo instala.

No decide por su cuenta si "tests que fallan" cuenta como fallo de la
herramienta (Verifier, Fase 7, lo trataría como tarea fallida y
reintentaría) -- ejecutar la suite correctamente y que dé resultados
en rojo es un éxito de la herramienta (hizo su trabajo), no un fallo
técnico. El resultado deja bien explícito cuántos tests pasaron y
cuántos fallaron para que el modelo (o el propio Danny) lo interprete.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from tools.base_tool import BaseTool
from security.path_guard import PathGuard

LIMITE_SALIDA = 4000  # no devolver salidas gigantes al modelo


class TestRunnerTool(BaseTool):

    name = "run_tests"

    description = (
        "Ejecuta las pruebas automatizadas de un proyecto o archivo "
        "(pytest si está instalado, si no unittest) y resume cuántas "
        "pasaron y cuántas fallaron."
    )

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Carpeta o archivo de pruebas (por defecto, el directorio actual).",
            },
            "pattern": {
                "type": "string",
                "description": "Patrón de archivos de test para unittest, si pytest no está instalado (por defecto 'test_*.py').",
            },
        },
        "required": [],
    }

    def execute(self, path: str = ".", pattern: str = "test_*.py"):

        ruta = Path(path)

        if not ruta.exists():
            return f"ERROR: la ruta no existe: {path}"

        permitido, motivo = PathGuard().validate(path)

        if not permitido:
            return (
                f"ERROR: {motivo} (ejecutar pruebas en una ruta fuera del "
                "área de trabajo equivale a ejecutar código arbitrario ahí, "
                "no está permitido)."
            )

        if self._pytest_disponible():
            return self._ejecutar_pytest(ruta)

        return self._ejecutar_unittest(ruta, pattern)

    def _pytest_disponible(self) -> bool:

        try:
            import importlib.util
            return importlib.util.find_spec("pytest") is not None
        except Exception:
            return False

    def _ejecutar_pytest(self, ruta: Path) -> str:

        try:

            resultado = subprocess.run(
                ["python3", "-m", "pytest", str(ruta), "-q"],
                capture_output=True, text=True, timeout=120,
            )

            return self._resumir("pytest", resultado)

        except Exception as e:

            return f"ERROR ejecutando pytest: {e}"

    def _ejecutar_unittest(self, ruta: Path, pattern: str) -> str:

        try:

            if ruta.is_file():
                directorio_inicio = str(ruta.parent)
                patron = ruta.name
            else:
                directorio_inicio = str(ruta)
                patron = pattern

            comando = [
                "python3", "-m", "unittest", "discover",
                "-s", directorio_inicio, "-p", patron, "-v",
            ]

            resultado = subprocess.run(
                comando, capture_output=True, text=True, timeout=120,
            )

            return self._resumir("unittest", resultado)

        except Exception as e:

            return f"ERROR ejecutando unittest: {e}"

    def _resumir(self, motor: str, resultado) -> str:

        salida = (resultado.stdout + "\n" + resultado.stderr).strip()

        if len(salida) > LIMITE_SALIDA:
            salida = salida[-LIMITE_SALIDA:]
            salida = "(...salida recortada...)\n" + salida

        estado = "OK: todas las pruebas pasaron" if resultado.returncode == 0 else "FALLOS: hay pruebas que no pasaron"

        return f"[{motor}] {estado}\n\n{salida}"
