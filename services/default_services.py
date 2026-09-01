"""
ARUS
Servicios por defecto.
"""

from __future__ import annotations

from database.database import Database
from events.event_bus import EventBus
from services.service_manager import ServiceManager


def load_default_services(
    manager: ServiceManager,
):

    manager.register(
        "database",
        Database(),
    )


    manager.register(
        "event_bus",
        EventBus(),
    )
