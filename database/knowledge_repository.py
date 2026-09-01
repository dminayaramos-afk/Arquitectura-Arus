"""
Repositorio de conocimiento.
"""

from __future__ import annotations

from database.repository import Repository


class KnowledgeRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            key TEXT UNIQUE,

            value TEXT

        )
        """)

        self.database.commit()
