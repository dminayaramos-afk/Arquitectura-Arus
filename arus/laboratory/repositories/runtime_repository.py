
"""
ARUS
Runtime Repository
"""

import sqlite3
from pathlib import Path


class RuntimeRepository:


    def __init__(
        self,
        database="database/arus.db"
    ):

        self.database = database

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
        CREATE TABLE IF NOT EXISTS laboratory_runtimes
        (

            id TEXT PRIMARY KEY,

            laboratory TEXT,

            state TEXT,

            session_id TEXT,

            started_at TEXT,

            stopped_at TEXT

        )
        """
        )

        self.connection.commit()



    def save(self, runtime):

        session = runtime.session


        self.connection.execute(
        """
        INSERT OR REPLACE INTO laboratory_runtimes
        VALUES (?,?,?,?,?,?)
        """,
        (
            session.id,
            runtime.laboratory.name,
            runtime.state.value,
            session.id,
            session.started_at.isoformat(),
            (
                session.finished_at.isoformat()
                if session.finished_at
                else None
            )
        )
        )


        self.connection.commit()



    def list(self):

        cursor = self.connection.execute(
            """
            SELECT *
            FROM laboratory_runtimes
            ORDER BY started_at
            """
        )

        return cursor.fetchall()



    def delete(self,id):

        self.connection.execute(
            """
            DELETE FROM laboratory_runtimes
            WHERE id=?
            """,
            (id,)
        )

        self.connection.commit()
