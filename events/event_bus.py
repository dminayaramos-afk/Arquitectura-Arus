"""
ARUS
Event Bus
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable

from events.event import Event


class EventBus:

    def __init__(self):

        self._listeners = defaultdict(list)

    def subscribe(
        self,
        event_name: str,
        callback: Callable[[Event], None],
    ) -> None:

        self._listeners[event_name].append(callback)

    def publish(
        self,
        event: Event,
    ) -> None:

        for callback in self._listeners[event.name]:
            callback(event)
