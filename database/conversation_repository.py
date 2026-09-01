"""
Repositorio de conversaciones.
"""

from __future__ import annotations

from database.repository import Repository


class ConversationRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            role TEXT NOT NULL,

            message TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.database.commit()

    def add(self, role: str, message: str):

        self.cursor.execute(

            "INSERT INTO conversations(role,message) VALUES(?,?)",

            (role, message),

        )

        self.database.commit()
