"""
ARUS
Registro de plugins.
"""

from __future__ import annotations

from plugins.plugin import Plugin


class PluginRegistry:


    def __init__(self):

        self.plugins: dict[str, Plugin] = {}


    def register(
        self,
        plugin: Plugin,
    ):

        self.plugins[plugin.name] = plugin


    def get(
        self,
        name: str,
    ):

        return self.plugins.get(name)


    def all(self):

        return self.plugins.values()
