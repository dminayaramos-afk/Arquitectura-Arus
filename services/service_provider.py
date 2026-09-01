"""
ARUS
Service Provider
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from services.container import ServiceContainer


class ServiceProvider(ABC):


    @abstractmethod
    def register(
        self,
        container: ServiceContainer,
    ):
        pass
