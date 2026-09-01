"""
ARUS
Service Container

Contenedor central de servicios.
"""

from __future__ import annotations


class ServiceContainer:


    def __init__(self):

        self.services = {}


    def register(
        self,
        name: str,
        service,
    ):

        self.services[name] = service


    def get(
        self,
        name: str,
    ):

        return self.services.get(name)


    def has(
        self,
        name: str,
    ) -> bool:

        return name in self.services
