"""
ARUS
Plugin base.

Fase 15: se añade `get_tools()` como hook OPCIONAL (no abstracto, no
rompe `plugins/examples/test_plugin.py` ni ningún plugin existente
que no lo implemente) para que un plugin pueda contribuir herramientas
reales al ToolManager (punto 42 del prompt maestro: "los plugins
podrán añadir herramientas; agentes; proveedores; comandos").

Alcance de esta fase: solo herramientas (`get_tools()`). Agentes,
proveedores de modelo y comandos no tienen un hook aquí todavía --
se podría añadir con el mismo patrón (get_agents(), get_commands()...)
cuando haga falta de verdad, en vez de crear ganchos especulativos
sin nadie que los use.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Plugin(ABC):

    name = "base"

    version = "1.0.0"


    @abstractmethod
    def initialize(self) -> None:
        """
        Inicializa el plugin.
        """
        pass


    def shutdown(self) -> None:
        """
        Cierre opcional del plugin.
        """
        pass

    def get_tools(self) -> list:
        """
        Hook opcional: devuelve una lista de instancias de BaseTool
        que este plugin quiere añadir a ARUS. Por defecto, ninguna.
        """
        return []
