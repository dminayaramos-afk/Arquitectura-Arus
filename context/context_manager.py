"""
ARUS
Context Manager

Gestiona el contexto entre memoria,
conversación y modelo IA.

Responsabilidad de ContextManager (Fase 3):
    Preparar y limitar el contexto (turnos recientes) que se le
    entrega al razonamiento/modelo para UNA conversación concreta.

Lo que NO hace ContextManager (para no duplicar responsabilidades):
    - No persiste conversaciones ni mensajes: eso es
      conversations.ConversationManager (Fase 2). Cuando se le pasa
      un ConversationManager, ContextManager delega ahí el guardado
      y la reconstrucción de contexto de conversaciones antiguas.
    - No decide qué se convierte en memoria a largo plazo: eso es
      memory.MemoryManager / Brain.
    - No llama al modelo de IA: eso es Fase 4
      (Chat -> Brain -> ModelManager). El parámetro opcional
      `summarizer` es un punto de extensión para que, en la Fase 4,
      Brain pueda inyectar un resumen generado por el modelo; si no
      se proporciona, se usa un resumen de emergencia sin IA para no
      perder información.

Compatibilidad: add_user_message / add_assistant_message / get_context /
clear siguen funcionando exactamente igual que antes (sin argumentos),
operando sobre una conversación "default" — así no se rompe ningún uso
existente de esta clase.
"""

from __future__ import annotations

from typing import Callable, Optional

from context.context_window import ContextWindow

_DEFAULT_CONVERSATION = "default"


class ContextManager:

    def __init__(
        self,
        max_messages: int = 20,
        max_chars: int = 12000,
        conversation_manager=None,
        summarizer: Optional[Callable[[list[dict]], str]] = None,
    ):

        self.max_messages = max_messages
        self.max_chars = max_chars

        # Delegado opcional para persistencia (Fase 2). Si no se
        # proporciona, ContextManager funciona igual que antes, solo
        # en memoria (sin persistencia).
        self.conversation_manager = conversation_manager

        # Punto de extensión para Fase 4 (resumen generado por IA).
        self.summarizer = summarizer

        self._windows: dict[str, ContextWindow] = {
            _DEFAULT_CONVERSATION: ContextWindow(max_messages)
        }

    # ------------------------------------------------------------------
    # API original (retrocompatible, opera sobre la conversación "default")
    # ------------------------------------------------------------------

    def add_user_message(self, message: str, conversation_id: Optional[str] = None):

        self.add_message("user", message, conversation_id)

    def add_assistant_message(self, message: str, conversation_id: Optional[str] = None):

        self.add_message("assistant", message, conversation_id)

    def get_context(self, conversation_id: Optional[str] = None) -> list[dict]:

        window = self._get_window(conversation_id)

        return window.get_all()

    def clear(self, conversation_id: Optional[str] = None):

        window = self._get_window(conversation_id)

        window.clear()

    # ------------------------------------------------------------------
    # Multi-conversación (Fase 3)
    # ------------------------------------------------------------------

    def _get_window(self, conversation_id: Optional[str]) -> ContextWindow:

        cid = conversation_id or _DEFAULT_CONVERSATION

        if cid not in self._windows:
            self._windows[cid] = ContextWindow(self.max_messages)

        return self._windows[cid]

    def add_message(self, role: str, content: str, conversation_id: Optional[str] = None) -> str:
        """
        Añade un turno al contexto en memoria de esa conversación y,
        si hay un ConversationManager conectado, lo persiste ahí
        (sin duplicar el almacenamiento: ContextManager no guarda
        nada en SQLite por su cuenta).
        """

        cid = conversation_id or _DEFAULT_CONVERSATION

        window = self._get_window(cid)

        window.add(role, content)

        if self.conversation_manager is not None and cid != _DEFAULT_CONVERSATION:

            try:
                self.conversation_manager.save(role, content, conversation_id=cid)
            except Exception:
                # La conversación en memoria sigue siendo válida aunque
                # falle la persistencia (p.ej. DB no disponible); no se
                # pierde el turno en curso.
                pass

        if self.needs_compaction(cid):
            self.compact(cid)

        return cid

    def resume(self, conversation_id: str, limit: Optional[int] = None) -> list[dict]:
        """
        Reconstruye el contexto en memoria de una conversación ya
        persistida (Fase 2), en lugar de tratarla como nueva
        (punto 4 del prompt maestro). No funciona sin
        ConversationManager conectado.
        """

        if self.conversation_manager is None:
            raise RuntimeError(
                "ContextManager.resume() requiere un ConversationManager conectado."
            )

        session = self.conversation_manager.resume(conversation_id)

        if session is None:
            return []

        window = ContextWindow(self.max_messages)

        messages = session.get("messages", [])

        take = messages[-limit:] if limit else messages

        for message in take:
            window.add(message["role"], message["content"])

        self._windows[conversation_id] = window

        return window.get_all()

    def needs_compaction(self, conversation_id: Optional[str] = None) -> bool:

        window = self._get_window(conversation_id)

        if len(window) >= self.max_messages:
            return True

        total_chars = sum(len(m["content"]) for m in window.get_all())

        return total_chars >= self.max_chars

    def compact(self, conversation_id: Optional[str] = None):
        """
        Reduce el contexto cuando crece demasiado (punto 9 del prompt
        maestro), conservando la conversación disponible para
        continuar sin reenviar siempre todo el historial al modelo.

        Sin un `summarizer` real (eso llega en Fase 4 vía Brain), se
        usa un resumen de emergencia: se guardan los primeros y
        últimos mensajes como referencia y se recorta el resto, en
        vez de perder la conversación entera o bloquear el sistema.
        """

        cid = conversation_id or _DEFAULT_CONVERSATION

        window = self._get_window(cid)

        messages = window.get_all()

        if not messages:
            return

        if self.summarizer is not None:
            summary = self.summarizer(messages)
        else:
            head = messages[0]["content"][:200]
            tail = messages[-1]["content"][:200]
            summary = (
                f"[Resumen automático de emergencia, sin IA] "
                f"Conversación con {len(messages)} turnos. "
                f"Empezó con: \"{head}\". Turno más reciente: \"{tail}\"."
            )

        if self.conversation_manager is not None and cid != _DEFAULT_CONVERSATION:
            try:
                self.conversation_manager.set_summary(cid, summary)
            except Exception:
                pass

        kept = max(self.max_messages // 2, 1)

        window.messages = window.get_all()[-kept:]

    def to_prompt(self, conversation_id: Optional[str] = None) -> str:
        """
        Da formato de texto al contexto actual usando ContextBuilder
        (ya existente en context/context_builder.py), para no
        duplicar esa lógica de formateo.
        """

        from context.context_builder import ContextBuilder

        return ContextBuilder().build(self.get_context(conversation_id))
