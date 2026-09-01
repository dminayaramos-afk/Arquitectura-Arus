"""
ARUS
Tool Manager
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import tools

from tools.base_tool import BaseTool


class ToolManager:

    def __init__(self):

        self.tools = {}

        self.load_tools()


    def load_tools(self):

        for _, module_name, _ in pkgutil.iter_modules(tools.__path__):

            if module_name in (
                "base_tool",
                "tool_manager",
            ):
                continue

            module = importlib.import_module(
                f"tools.{module_name}"
            )

            for _, obj in inspect.getmembers(
                module,
                inspect.isclass,
            ):

                if (
                    issubclass(obj, BaseTool)
                    and obj is not BaseTool
                ):

                    tool = obj()

                    self.tools[tool.name] = tool


    def register(self, tool):
        """
        Fase 15: permite añadir una herramienta ya instanciada (p.ej.
        aportada por un plugin) sin pasar por el escaneo de
        `tools/`. No sustituye `load_tools()` -- es aditivo.
        """

        self.tools[tool.name] = tool


    def execute(
        self,
        name,
        *args,
        **kwargs,
    ):

        if name not in self.tools:

            raise ValueError(
                f"Herramienta '{name}' no encontrada."
            )

        return self.tools[name].execute(
            *args,
            **kwargs,
        )


    def available_tools(self):

        return sorted(
            self.tools.keys()
        )


    def schemas(self):

        return [
            tool.schema()
            for tool in self.tools.values()
        ]


    def tool_prompt(self):

        text = "Herramientas disponibles:\n\n"

        for tool in self.tools.values():

            text += (
                f"- {tool.name}: "
                f"{tool.description}\n"
            )

        return text
