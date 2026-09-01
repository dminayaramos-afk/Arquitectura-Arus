"""
ARUS
Service Manager

Gestiona la carga de servicios.
"""

from __future__ import annotations

from services.container import ServiceContainer


class ServiceManager:


    def __init__(self):

        self.container = ServiceContainer()


    def register(
        self,
        name: str,
        service,
    ):

        self.container.register(
            name,
            service,
        )


    def get(
        self,
        name: str,
    ):

        return self.container.get(name)
