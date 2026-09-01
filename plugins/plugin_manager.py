"""
ARUS
Gestor de plugins (Fase 15, punto 42 del prompt maestro)

Antes: `load()` exigía que alguien construyera el objeto Plugin a
mano y lo pasara; nada descubría plugins automáticamente, y nada en
el proyecto instanciaba `PluginManager` (auditado antes de tocar
nada). Ahora hay descubrimiento automático real, en el mismo patrón
que `tools/tool_manager.py` ya usa para escanear `tools/`.

Seguridad (punto 42: "Los plugins no deben tener acceso ilimitado al
sistema"): esto NO implementa un sandbox de ejecución real para el
código de un plugin -- eso necesitaría un entorno de ejecución
restringido de verdad (procesos separados, límites de recursos), que
está fuera del alcance de esta fase y no se finge aquí. Lo que sí se
garantiza:
  - Solo se cargan plugins desde una carpeta explícita
    (`plugins/installed/` por defecto) -- no desde cualquier ruta que
    alguien indique en caliente.
  - Un plugin que falla al cargar NO tumba a ARUS ni a los demás
    plugins (fallo contenido, punto 45: no reventar por un error).
  - Cada carga (éxito o fallo) queda registrada en auditoría
    (AuditLogger, punto 41).
  - Las herramientas que aporta un plugin se ejecutan a través del
    mismo `ToolManager` que todo lo demás -- si en el futuro
    ToolManager añade límites de permisos por herramienta, se
    aplicarían igual a las de un plugin.
"""

from __future__ import annotations

import importlib
import importlib.util
import inspect
import pkgutil
from pathlib import Path
from typing import Optional

from plugins.plugin import Plugin
from plugins.plugin_registry import PluginRegistry
from security.audit_logger import AuditLogger

DIRECTORIO_POR_DEFECTO = "plugins/installed"


class PluginManager:

    def __init__(self):

        self.registry = PluginRegistry()

        self.audit = AuditLogger()

        self.failed: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Carga manual (retrocompatible con el PluginManager anterior)
    # ------------------------------------------------------------------

    def load(self, plugin: Plugin, tool_manager=None):

        plugin.initialize()

        self.registry.register(plugin)

        if tool_manager is not None:
            for tool in plugin.get_tools():
                tool_manager.register(tool)

        self.audit.log(
            tool="plugin_manager",
            arguments={"action": "load", "plugin": plugin.name},
            result="OK",
        )

    def unload(self, name: str):

        plugin = self.registry.get(name)

        if plugin:

            plugin.shutdown()

            self.audit.log(
                tool="plugin_manager",
                arguments={"action": "unload", "plugin": name},
                result="OK",
            )

    # ------------------------------------------------------------------
    # Descubrimiento automático (Fase 15)
    # ------------------------------------------------------------------

    def discover(self, directory: str = DIRECTORIO_POR_DEFECTO) -> list[type]:
        """Devuelve las clases Plugin encontradas en `directory` (sin instanciarlas)."""

        ruta = Path(directory)

        if not ruta.exists():
            return []

        encontradas = []

        for archivo in sorted(ruta.glob("*.py")):

            if archivo.name == "__init__.py":
                continue

            spec = importlib.util.spec_from_file_location(
                f"plugins.installed.{archivo.stem}", archivo
            )

            try:

                modulo = importlib.util.module_from_spec(spec)

                spec.loader.exec_module(modulo)

            except Exception as e:

                self.failed[archivo.stem] = f"Error al importar: {e}"

                self.audit.log(
                    tool="plugin_manager",
                    arguments={"action": "discover", "file": str(archivo)},
                    result=f"ERROR: {e}",
                )

                continue

            for _, obj in inspect.getmembers(modulo, inspect.isclass):

                if issubclass(obj, Plugin) and obj is not Plugin:
                    encontradas.append(obj)

        return encontradas

    def load_all(self, directory: str = DIRECTORIO_POR_DEFECTO, tool_manager=None) -> dict:
        """
        Descubre y carga todos los plugins de `directory`. Un plugin
        que falla no impide que se carguen los demás. Devuelve un
        resumen: {"loaded": [...], "failed": {nombre: motivo}}.
        """

        self.failed = {}

        cargados = []

        for clase in self.discover(directory):

            nombre = getattr(clase, "name", clase.__name__)

            try:

                instancia = clase()

                self.load(instancia, tool_manager=tool_manager)

                cargados.append(nombre)

            except Exception as e:

                self.failed[nombre] = str(e)

                self.audit.log(
                    tool="plugin_manager",
                    arguments={"action": "load", "plugin": nombre},
                    result=f"ERROR: {e}",
                )

        return {"loaded": cargados, "failed": dict(self.failed)}
