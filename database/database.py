"""
ARUS - Artificial Reasoning Unified System
------------------------------------------

Gestor central de la base de datos SQLite.

Este módulo será el único responsable de abrir y gestionar
la conexión con SQLite.

Ningún otro módulo deberá conectarse directamente.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from arus.core.logger import get_logger
from arus.core.paths import DATA_DIR

logger = get_logger(__name__)


class Database:

    def __init__(self):

        DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.database_file = DATA_DIR / "arus.db"

        self.connection = sqlite3.connect(
            self.database_file
        )

        self.connection.row_factory = sqlite3.Row

        logger.info(
            "SQLite inicializado."
        )

    def cursor(self):

        return self.connection.cursor()

    def commit(self):

        self.connection.commit()

    def close(self):

        self.connection.close()

        logger.info(
            "SQLite cerrado."
        )
