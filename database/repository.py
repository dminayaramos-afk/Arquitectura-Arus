"""
Repositorio base.
"""

from __future__ import annotations

from database.database import Database


class Repository:

    def __init__(self, database: Database):

        self.database = database

        self.cursor = database.cursor()
