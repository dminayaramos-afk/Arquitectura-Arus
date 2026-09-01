"""
ARUS
Event Handler
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from events.event import Event


class EventHandler(ABC):

    @abstractmethod
    def handle(
        self,
        event: Event,
    ) -> None:
        ...
