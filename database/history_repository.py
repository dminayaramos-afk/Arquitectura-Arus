"""
Repositorio del historial.
"""

from __future__ import annotations

from database.repository import Repository


class HistoryRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            command TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.database.commit()
