"""
ARUS
Virtual Laboratory
Configuration Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LaboratoryConfiguration:
    """
    Configuración general de un laboratorio virtual.
    """

    allow_network: bool = False

    allow_filesystem: bool = True

    allow_python: bool = True

    allow_shell: bool = False

    max_workspaces: int = 10

    max_experiments: int = 100

    autosave: bool = True

    autosave_interval: int = 300

    environment: str = "development"

    variables: Dict[str, str] = field(default_factory=dict)

    enabled_modules: List[str] = field(default_factory=list)

    def enable_module(self, module: str):

        if module not in self.enabled_modules:
            self.enabled_modules.append(module)

    def disable_module(self, module: str):

        if module in self.enabled_modules:
            self.enabled_modules.remove(module)

    def set_variable(self, key: str, value: str):

        self.variables[key] = value

    def get_variable(self, key: str, default=None):

        return self.variables.get(key, default)

    def to_dict(self):

        return {
            "allow_network": self.allow_network,
            "allow_filesystem": self.allow_filesystem,
            "allow_python": self.allow_python,
            "allow_shell": self.allow_shell,
            "max_workspaces": self.max_workspaces,
            "max_experiments": self.max_experiments,
            "autosave": self.autosave,
            "autosave_interval": self.autosave_interval,
            "environment": self.environment,
            "variables": self.variables,
            "enabled_modules": self.enabled_modules,
        }
