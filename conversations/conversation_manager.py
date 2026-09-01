"""
ARUS
Conversation Manager
---------------------

Infraestructura para que la futura interfaz (panel de "Conversaciones
recientes") pueda crear, guardar, cargar, reanudar, buscar, renombrar,
archivar, marcar como favorita y eliminar conversaciones.

Este módulo NO contiene ningún código de interfaz. Solo expone una API
que la GUI podrá llamar cuando el propietario del proyecto construya
ese panel.

Separación deliberada respecto a memory/:
    - conversations/  -> historial de turnos de una conversación concreta
                          (lo que se dijo).
    - memory/          -> conocimiento que debe sobrevivir entre
                          conversaciones (lo que se debe recordar).

ConversationManager no decide qué se convierte en memoria persistente;
eso es responsabilidad de MemoryManager / Brain (ver punto 5 y 6 del
prompt maestro). Este módulo solo persiste la conversación en sí,
de forma incremental, para no perder nada si ARUS se cierra o falla.
"""

from __future__ import annotations

from typing import Any, Optional

from database.database import Database
from database.conversation_session_repository import ConversationSessionRepository


class ConversationManager:
    """Punto único de acceso a la persistencia de conversaciones."""

    def __init__(self, database: Optional[Database] = None):

        self.database = database or Database()

        self.repo = ConversationSessionRepository(self.database)

        self.repo.create_table()

        # Conversación activa en memoria (la que está en curso ahora).
        self._active_id: Optional[str] = None

    # ------------------------------------------------------------------
    # Ciclo de vida de la conversación activa
    # ------------------------------------------------------------------

    def create(self, title: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """Crea una nueva conversación y la deja como activa."""

        conversation_id = self.repo.create(title=title, metadata=metadata)

        self._active_id = conversation_id

        return conversation_id

    def active_id(self) -> Optional[str]:

        return self._active_id

    def ensure_active(self) -> str:
        """Devuelve la conversación activa, creando una nueva si no existe."""

        if not self._active_id:
            return self.create()

        return self._active_id

    def save(self, role: str, content: str, conversation_id: Optional[str] = None):
        """
        Guardado incremental de un turno (mensaje) de la conversación.

        Se llama tras cada mensaje, no solo al cerrar la conversación,
        para que nada se pierda si ARUS falla, se cierra o pierde
        conexión (punto 3 del prompt maestro).
        """

        cid = conversation_id or self.ensure_active()

        self.repo.add_message(cid, role, content)

        return cid

    def close(self, conversation_id: Optional[str] = None):
        """
        Marca el final de una conversación. No borra nada: el
        guardado ya es incremental, así que 'cerrar' solo limpia el
        puntero de conversación activa.
        """

        cid = conversation_id or self._active_id

        if cid == self._active_id:
            self._active_id = None

        return cid

    # ------------------------------------------------------------------
    # Carga / reanudación
    # ------------------------------------------------------------------

    def load(self, conversation_id: str) -> Optional[dict]:
        """Devuelve la sesión (metadatos) y sus mensajes."""

        session = self.repo.get(conversation_id)

        if not session:
            return None

        session["messages"] = self.repo.messages(conversation_id)

        return session

    def resume(self, conversation_id: str) -> Optional[dict]:
        """
        Reconstruye el contexto de una conversación antigua y la deja
        como activa, para que ARUS continúe sin tratarla como nueva
        (punto 4 del prompt maestro).
        """

        session = self.load(conversation_id)

        if session is None:
            return None

        self._active_id = conversation_id

        self.repo.touch(conversation_id)

        return session

    # ------------------------------------------------------------------
    # Listado / búsqueda
    # ------------------------------------------------------------------

    def recent(self, limit: int = 20, include_archived: bool = False) -> list[dict]:

        return self.repo.recent(limit=limit, include_archived=include_archived)

    def search(self, query: str) -> list[dict]:

        return self.repo.search(query)

    # ------------------------------------------------------------------
    # Gestión
    # ------------------------------------------------------------------

    def rename(self, conversation_id: str, title: str):

        self.repo.rename(conversation_id, title)

    def delete(self, conversation_id: str):

        if conversation_id == self._active_id:
            self._active_id = None

        self.repo.delete(conversation_id)

    def archive(self, conversation_id: str, archived: bool = True):

        self.repo.set_archived(conversation_id, archived)

    def favorite(self, conversation_id: str, favorite: bool = True):

        self.repo.set_favorite(conversation_id, favorite)

    def set_summary(self, conversation_id: str, summary: str):
        """
        Guarda el resumen automático de la conversación (punto 47).
        El generador de resúmenes en sí (Context Manager / Brain) no
        vive aquí; este método solo lo persiste.
        """

        self.repo.set_summary(conversation_id, summary)

    def set_metadata(self, conversation_id: str, metadata: dict):

        self.repo.set_metadata(conversation_id, metadata)
