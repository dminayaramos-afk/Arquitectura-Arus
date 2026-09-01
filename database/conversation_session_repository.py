"""
ARUS
Conversation Session Repository

Tabla nueva para sesiones de conversación completas
(title, summary, metadata, favorite, archived).

No sustituye ni modifica la tabla legacy 'conversations'
(ConversationRepository), que se deja intacta para no romper
nada que ya dependa de ella.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from database.repository import Repository


class ConversationSessionRepository(Repository):

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_sessions(

            id TEXT PRIMARY KEY,

            title TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            summary TEXT,

            metadata TEXT,

            favorite INTEGER DEFAULT 0,

            archived INTEGER DEFAULT 0
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_messages(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id TEXT NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(conversation_id) REFERENCES conversation_sessions(id)
        )
        """)

        self.database.commit()

    # ------------------------------------------------------------------
    # Sesiones
    # ------------------------------------------------------------------

    def create(self, title: Optional[str] = None, metadata: Optional[dict] = None) -> str:

        conversation_id = str(uuid.uuid4())

        self.cursor.execute(
            "INSERT INTO conversation_sessions(id, title, metadata) VALUES (?, ?, ?)",
            (conversation_id, title or "Nueva conversación", json.dumps(metadata or {})),
        )

        self.database.commit()

        return conversation_id

    def touch(self, conversation_id: str):

        self.cursor.execute(
            "UPDATE conversation_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,),
        )

        self.database.commit()

    def get(self, conversation_id: str) -> Optional[dict]:

        self.cursor.execute(
            "SELECT * FROM conversation_sessions WHERE id = ?",
            (conversation_id,),
        )

        row = self.cursor.fetchone()

        return dict(row) if row else None

    def rename(self, conversation_id: str, title: str):

        self.cursor.execute(
            "UPDATE conversation_sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (title, conversation_id),
        )

        self.database.commit()

    def set_summary(self, conversation_id: str, summary: str):

        self.cursor.execute(
            "UPDATE conversation_sessions SET summary = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (summary, conversation_id),
        )

        self.database.commit()

    def set_metadata(self, conversation_id: str, metadata: dict):

        self.cursor.execute(
            "UPDATE conversation_sessions SET metadata = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (json.dumps(metadata), conversation_id),
        )

        self.database.commit()

    def set_favorite(self, conversation_id: str, favorite: bool):

        self.cursor.execute(
            "UPDATE conversation_sessions SET favorite = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (1 if favorite else 0, conversation_id),
        )

        self.database.commit()

    def set_archived(self, conversation_id: str, archived: bool):

        self.cursor.execute(
            "UPDATE conversation_sessions SET archived = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (1 if archived else 0, conversation_id),
        )

        self.database.commit()

    def delete(self, conversation_id: str):

        self.cursor.execute(
            "DELETE FROM conversation_messages WHERE conversation_id = ?",
            (conversation_id,),
        )

        self.cursor.execute(
            "DELETE FROM conversation_sessions WHERE id = ?",
            (conversation_id,),
        )

        self.database.commit()

    def recent(self, limit: int = 20, include_archived: bool = False) -> list[dict]:

        query = "SELECT * FROM conversation_sessions"

        if not include_archived:
            query += " WHERE archived = 0"

        query += " ORDER BY updated_at DESC LIMIT ?"

        self.cursor.execute(query, (limit,))

        return [dict(row) for row in self.cursor.fetchall()]

    def search(self, text: str) -> list[dict]:

        like = f"%{text}%"

        self.cursor.execute(
            """
            SELECT DISTINCT s.* FROM conversation_sessions s
            LEFT JOIN conversation_messages m ON m.conversation_id = s.id
            WHERE s.title LIKE ? OR s.summary LIKE ? OR m.content LIKE ?
            ORDER BY s.updated_at DESC
            """,
            (like, like, like),
        )

        return [dict(row) for row in self.cursor.fetchall()]

    # ------------------------------------------------------------------
    # Mensajes
    # ------------------------------------------------------------------

    def add_message(self, conversation_id: str, role: str, content: str):

        self.cursor.execute(
            "INSERT INTO conversation_messages(conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content),
        )

        self.database.commit()

        self.touch(conversation_id)

    def messages(self, conversation_id: str) -> list[dict]:

        self.cursor.execute(
            "SELECT * FROM conversation_messages WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,),
        )

        return [dict(row) for row in self.cursor.fetchall()]
