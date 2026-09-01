"""
Repositorio de configuración.
"""

from __future__ import annotations

from database.repository import Repository


class SettingsRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings(

            key TEXT PRIMARY KEY,

            value TEXT

        )
        """)

        self.database.commit()
