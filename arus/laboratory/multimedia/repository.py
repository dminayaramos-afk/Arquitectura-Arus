
"""
ARUS
Multimedia Repository
"""

import sqlite3
from pathlib import Path


class MultimediaRepository:


    def __init__(
        self,
        database="database/arus.db"
    ):

        Path(database).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.connection = sqlite3.connect(
            database
        )

        self.connection.row_factory = sqlite3.Row

        self.create_table()



    def create_table(self):

        self.connection.execute(
        """
        CREATE TABLE IF NOT EXISTS multimedia
        (

            id TEXT PRIMARY KEY,

            name TEXT,

            path TEXT,

            type TEXT,

            metadata TEXT

        )
        """
        )

        self.connection.commit()



    def save(self, media):

        self.connection.execute(
        """
        INSERT OR REPLACE INTO multimedia
        VALUES(?,?,?,?,?)
        """,
        (
            media.id,
            media.name,
            media.path,
            media.type.value,
            str(media.metadata)
        )
        )

        self.connection.commit()



    def list(self):

        cursor = self.connection.execute(
        """
        SELECT *
        FROM multimedia
        """
        )

        return cursor.fetchall()
