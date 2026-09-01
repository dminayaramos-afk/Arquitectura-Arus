
"""
ARUS
Agent Repository
"""

import sqlite3
from pathlib import Path


class AgentRepository:


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
        CREATE TABLE IF NOT EXISTS laboratory_agents
        (

            id TEXT PRIMARY KEY,

            name TEXT UNIQUE,

            role TEXT,

            status TEXT,

            tasks TEXT

        )
        """
        )

        self.connection.commit()



    def save(
        self,
        agent
    ):

        self.connection.execute(
        """
        INSERT OR REPLACE INTO laboratory_agents
        VALUES(?,?,?,?,?)
        """,
        (
            agent.id,
            agent.name,
            agent.role,
            agent.status.value,
            str(agent.tasks)
        )
        )

        self.connection.commit()



    def list(self):

        cursor = self.connection.execute(
            """
            SELECT *
            FROM laboratory_agents
            """
        )

        return cursor.fetchall()



    def delete(
        self,
        name
    ):

        self.connection.execute(
        """
        DELETE FROM laboratory_agents
        WHERE name=?
        """,
        (name,)
        )

        self.connection.commit()
