"""
ARUS
System Core

Coordinador principal.
"""

from __future__ import annotations

from services.default_services import load_default_services
from services.service_manager import ServiceManager


class System:


    def __init__(self):

        self.services = ServiceManager()


    def initialize(self):

        load_default_services(
            self.services
        )
