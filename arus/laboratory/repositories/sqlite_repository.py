"""
ARUS
Virtual Laboratory
SQLite Repository
"""

from __future__ import annotations

import sqlite3
import json
from pathlib import Path

from arus.laboratory.models.status import LaboratoryStatus
from arus.laboratory.interfaces import LaboratoryRepository


class SQLiteLaboratoryRepository(LaboratoryRepository):

    def __init__(
        self,
        database: str = "database/arus.db",
    ):

        self.database = database

        Path(database).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            self.database,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self._create_tables()

    def _create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS laboratories (

                id TEXT PRIMARY KEY,

                name TEXT UNIQUE NOT NULL,

                description TEXT,

                status TEXT,

                created_at TEXT,

                updated_at TEXT,

                owner TEXT,

                version TEXT,

                metadata TEXT,

                tags TEXT

            )
            """
        )



        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS workspaces (

                id TEXT PRIMARY KEY,

                laboratory TEXT NOT NULL,

                name TEXT NOT NULL,

                description TEXT,

                created_at TEXT,

                UNIQUE(laboratory,name)

            )
            """
        )


        self.connection.commit()

    def cursor(self):

        return self.connection.cursor()

    def commit(self):

        self.connection.commit()



    def save(self, laboratory):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO laboratories(
                id,
                name,
                description,
                status,
                created_at,
                updated_at,
                owner,
                version,
                metadata,
                tags
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                laboratory.id,
                laboratory.name,
                laboratory.description,
                laboratory.status.value,
                laboratory.created_at.isoformat(),
                laboratory.updated_at.isoformat(),
                laboratory.owner,
                laboratory.version,
                json.dumps(laboratory.metadata),
                json.dumps(laboratory.tags),
            ),
        )

        self.connection.commit()


    def exists(self, name):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT 1 FROM laboratories WHERE name=?",
            (name,),
        )

        return cursor.fetchone() is not None


    def delete(self, name):

        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM laboratories WHERE name=?",
            (name,),
        )

        self.connection.commit()


    def list(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM laboratories ORDER BY name"
        )

        return cursor.fetchall()


    def get(self, name):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM laboratories WHERE name=?",
            (name,),
        )

        return cursor.fetchone()




    def load(self, name, laboratory_class):

        row = self.get(name)

        if row is None:
            return None

        laboratory = laboratory_class(
            name=row["name"],
            description=row["description"] or "",
        )

        laboratory.id = row["id"]
        laboratory.owner = row["owner"]
        laboratory.version = row["version"]

        laboratory.status = LaboratoryStatus(
            row["status"]
        )

        laboratory.metadata = json.loads(
            row["metadata"] or "{}"
        )

        laboratory.tags = json.loads(
            row["tags"] or "[]"
        )

        return laboratory




    def save_workspace(
        self,
        laboratory,
        workspace,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO workspaces(
                id,
                laboratory,
                name,
                description,
                created_at
            )
            VALUES(?,?,?,?,?)
            """,
            (
                workspace.id,
                laboratory,
                workspace.name,
                workspace.description,
                workspace.created_at.isoformat(),
            ),
        )

        self.connection.commit()


    def list_workspaces(
        self,
        laboratory,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM workspaces
            WHERE laboratory=?
            """,
            (laboratory,),
        )

        return cursor.fetchall()


    def delete_workspaces(
        self,
        laboratory,
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            DELETE FROM workspaces
            WHERE laboratory=?
            """,
            (laboratory,),
        )

        self.connection.commit()


    def close(self):

        self.connection.close()