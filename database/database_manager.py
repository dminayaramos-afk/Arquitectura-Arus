"""
ARUS
Database Manager
"""

from __future__ import annotations

from database.conversation_repository import ConversationRepository
from database.database import Database
from database.history_repository import HistoryRepository
from database.knowledge_repository import KnowledgeRepository
from database.settings_repository import SettingsRepository


class DatabaseManager:

    def __init__(self):

        self.db = Database()

        self.conversations = ConversationRepository(self.db)

        self.knowledge = KnowledgeRepository(self.db)

        self.settings = SettingsRepository(self.db)

        self.history = HistoryRepository(self.db)

    def initialize(self):

        self.conversations.create_table()

        self.knowledge.create_table()

        self.settings.create_table()

        self.history.create_table()
