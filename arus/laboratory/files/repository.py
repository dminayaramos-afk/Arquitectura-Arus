"""
ARUS
File Repository
"""

import sqlite3
from pathlib import Path


class FileRepository:


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
        CREATE TABLE IF NOT EXISTS laboratory_files
        (

            id TEXT PRIMARY KEY,

            name TEXT,

            path TEXT,

            type TEXT,

            size INTEGER,

            hash TEXT,

            metadata TEXT

        )
        """
        )

        self.connection.commit()



    def save(
        self,
        file
    ):

        self.connection.execute(
        """
        INSERT OR REPLACE INTO laboratory_files
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            file.id,
            file.name,
            file.path,
            file.type.value,
            file.size,
            file.hash,
            str(file.metadata)
        )
        )

        self.connection.commit()



    def list(self):

        cursor = self.connection.execute(
        """
        SELECT *
        FROM laboratory_files
        """
        )

        return cursor.fetchall()
