"""
ARUS
Context Window

Gestiona la ventana de contexto utilizada por el Brain.
Mantiene únicamente los últimos mensajes para evitar
que el contexto crezca indefinidamente.
"""

from __future__ import annotations


class ContextWindow:
    """Ventana de contexto conversacional."""

    def __init__(self, limit: int = 20):

        self.limit = limit
        self.messages = []


    def add(
        self,
        role: str,
        content: str,
    ) -> None:

        self.messages.append(
            {
                "role": role,
                "content": content,
            }
        )

        self.trim()


    def get(self):

        return self.messages


    def get_all(self):

        return list(self.messages)


    def trim(self):

        if len(self.messages) > self.limit:
            self.messages = self.messages[-self.limit:]


    def clear(self):

        self.messages.clear()


    def __len__(self):

        return len(self.messages)
