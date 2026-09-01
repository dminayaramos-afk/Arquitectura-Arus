"""
ARUS
Persistent Memory
"""

from __future__ import annotations

from database.database_manager import DatabaseManager


class PersistentMemory:

    def __init__(self):

        self.database = DatabaseManager()

        self.database.initialize()

    def save_message(
        self,
        role: str,
        message: str,
    ):

        self.database.conversations.add(
            role,
            message,
        )
