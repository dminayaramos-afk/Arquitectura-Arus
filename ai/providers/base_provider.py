"""
Proveedor base de IA.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):

    name = "base"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
