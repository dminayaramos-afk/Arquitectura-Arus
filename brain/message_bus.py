"""
ARUS
Message Bus
"""

from __future__ import annotations

from collections import defaultdict

from brain.message import Message


class MessageBus:

    def __init__(self):

        self._queues = defaultdict(list)

    def send(
        self,
        message: Message,
    ):

        self._queues[
            message.receiver
        ].append(message)

    def receive(
        self,
        receiver: str,
    ):

        return self._queues.pop(
            receiver,
            [],
        )

    def pending(
        self,
        receiver: str,
    ):

        return len(
            self._queues.get(
                receiver,
                [],
            )
        )
