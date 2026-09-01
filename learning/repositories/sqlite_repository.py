from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

from learning.domain.knowledge import KnowledgeItem
from learning.domain.repository import KnowledgeRepository


DB = Path("database/learning.db")
DB.parent.mkdir(parents=True, exist_ok=True)


class SQLiteKnowledgeRepository(KnowledgeRepository):

    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS knowledge(
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            confidence REAL,
            version INTEGER,
            created_at TEXT,
            updated_at TEXT
        )
        """)
        self.conn.commit()

    def save(self,item:KnowledgeItem)->None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO knowledge
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                item.id,
                item.title,
                item.content,
                item.confidence,
                item.version,
                item.created_at.isoformat(),
                item.updated_at.isoformat(),
            )
        )
        self.conn.commit()

    def update(self,item):
        self.save(item)

    def get(self,item_id):

        r=self.conn.execute(
            "SELECT * FROM knowledge WHERE id=?",
            (item_id,)
        ).fetchone()

        if r is None:
            return None

        k=KnowledgeItem(
            title=r[1],
            content=r[2]
        )

        k.id=r[0]
        k.confidence=r[3]
        k.version=r[4]
        k.created_at=datetime.fromisoformat(r[5])
        k.updated_at=datetime.fromisoformat(r[6])

        return k

    def delete(self,item_id):
        cur=self.conn.execute(
            "DELETE FROM knowledge WHERE id=?",
            (item_id,)
        )
        self.conn.commit()
        return cur.rowcount>0

    def list(self):

        ids=self.conn.execute(
            "SELECT id FROM knowledge"
        ).fetchall()

        return [
            self.get(i[0])
            for i in ids
        ]

    def search(self,q):

        q="%"+q.lower()+"%"

        rows=self.conn.execute(
            """
            SELECT id
            FROM knowledge
            WHERE lower(title) LIKE ?
               OR lower(content) LIKE ?
            """,
            (q,q)
        ).fetchall()

        return [
            self.get(r[0])
            for r in rows
        ]

    def exists(self,item_id):
        return self.conn.execute(
            "SELECT 1 FROM knowledge WHERE id=?",
            (item_id,)
        ).fetchone() is not None

    def clear(self):
        self.conn.execute("DELETE FROM knowledge")
        self.conn.commit()
