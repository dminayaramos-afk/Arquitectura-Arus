"""
ARUS
Skill Loader

Carga automática de habilidades.
"""

from __future__ import annotations

import importlib
import pkgutil

import skills


class SkillLoader:


    def discover(self):

        found = []


        for module in pkgutil.walk_packages(
            skills.__path__,
            skills.__name__ + ".",
        ):

            try:

                imported = importlib.import_module(
                    module.name
                )

                found.append(
                    imported
                )

            except Exception:

                pass


        return found
