
"""
ARUS
Experiment Repository
"""

import sqlite3
from pathlib import Path


class ExperimentRepository:


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
        CREATE TABLE IF NOT EXISTS laboratory_experiments
        (
            id TEXT PRIMARY KEY,

            name TEXT,

            description TEXT,

            status TEXT,

            results TEXT
        )
        """
        )

        self.connection.commit()



    def save(
        self,
        experiment
    ):

        self.connection.execute(
        """
        INSERT OR REPLACE INTO laboratory_experiments
        VALUES(?,?,?,?,?)
        """,
        (
            experiment.id,
            experiment.name,
            experiment.description,
            experiment.status.value,
            str(experiment.results)
        )
        )

        self.connection.commit()



    def list(self):

        cursor = self.connection.execute(
        """
        SELECT *
        FROM laboratory_experiments
        """
        )

        return cursor.fetchall()
