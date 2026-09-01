"""
ARUS
Device Repository
"""

import sqlite3
from pathlib import Path


class DeviceRepository:


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
        CREATE TABLE IF NOT EXISTS devices
        (
            id TEXT PRIMARY KEY,

            name TEXT,

            type TEXT,

            status TEXT,

            metadata TEXT
        )
        """
        )

        self.connection.commit()



    def save(
        self,
        device
    ):

        self.connection.execute(
        """
        INSERT OR REPLACE INTO devices
        VALUES(?,?,?,?,?)
        """,
        (
            device.id,
            device.name,
            device.type.value,
            device.status.value,
            str(device.metadata)
        )
        )

        self.connection.commit()



    def list(self):

        cursor=self.connection.execute(
        """
        SELECT *
        FROM devices
        """
        )

        return cursor.fetchall()
