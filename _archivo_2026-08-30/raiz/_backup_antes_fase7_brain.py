"""
ARUS
Brain

FASE 5
Integra:

    Chat
      ↓
    Controller
      ↓
    Brain
      ↓
    ConversationManager
      ↓
    ContextManager
      ↓
    ModelManager
      ↓
    LocalProvider

La memoria existente (MemoryManager) se mantiene por
compatibilidad con el resto del sistema.

ConversationManager:
    Persiste el historial completo de la conversación.

ContextManager:
    Mantiene el contexto activo que se entrega al modelo
    y limita su tamaño.

MemoryManager:
    Mantiene la memoria existente de ARUS
    (working / long / persistent).
"""

from __future__ import annotations

from agents.agent_response import AgentResponse

from ai.model_manager import ModelManager
from memory.memory_manager import MemoryManager

from conversations.conversation_manager import ConversationManager
from context.context_manager import ContextManager

from tools.tool_manager import ToolManager
from brain.task_manager import TaskManager
from brain.planner import Planner

from security.permission_manager import PermissionManager
from security.audit_logger import AuditLogger
from security.rate_limiter import RateLimiter

from brain.intent_detector import IntentDetector

from agents.agent_request import AgentRequest
from agents.agent_registry import AgentRegistry
from agents.agent_router import AgentRouter
from agents.tool_agent import ToolAgent

from learning import learning_manager


class Brain:
    """
    Cerebro principal de ARUS.

    Fase 5 añade una conversación persistente real y un
    ContextManager conectado al ConversationManager.
    """

    def __init__(self):

        # --------------------------------------------------------
        # Modelo
        # --------------------------------------------------------

        self.model = ModelManager()

        # --------------------------------------------------------
        # Memoria existente
        # --------------------------------------------------------

        self.memory = MemoryManager()

        # --------------------------------------------------------
        # Conversaciones persistentes
        # --------------------------------------------------------

        self.conversations = ConversationManager()

        # Creamos una conversación activa para esta instancia
        # del Brain.
        self.conversation_id = self.conversations.create(
            title="Conversación ARUS"
        )

        # --------------------------------------------------------
        # Contexto
        # --------------------------------------------------------

        self.context = ContextManager(
            max_messages=20,
            max_chars=12000,
            conversation_manager=self.conversations,
        )

        # --------------------------------------------------------
        # Herramientas / planificación
        # --------------------------------------------------------

        self.tools = ToolManager()
        self.tasks = TaskManager()
        self.planner = Planner()

        # --------------------------------------------------------
        # Seguridad
        # --------------------------------------------------------

        self.permissions = PermissionManager()
        self.audit = AuditLogger()
        self.rate = RateLimiter()

        # --------------------------------------------------------
        # Intent Detector
        # --------------------------------------------------------

        self.intent_detector = IntentDetector()

        # --------------------------------------------------------
        # Agentes
        # --------------------------------------------------------

        self.registry = AgentRegistry()

        self.registry.register(
            "tool",
            ToolAgent(),
        )

        self.router = AgentRouter(
            self.registry
        )

    # ============================================================
    # CONVERSACIONES
    # ============================================================

    def new_conversation(self, title: str = "Conversación ARUS") -> str:
        """
        Crea una conversación nueva y limpia el contexto activo.
        """

        self.conversation_id = self.conversations.create(
            title=title
        )

        self.context.clear(self.conversation_id)

        return self.conversation_id

    def resume_conversation(self, conversation_id: str) -> bool:
        """
        Reanuda una conversación existente.

        El historial persistido se reconstruye mediante
        ConversationManager + ContextManager.
        """

        session = self.conversations.resume(
            conversation_id
        )

        if session is None:
            return False

        self.conversation_id = conversation_id

        self.context.resume(
            conversation_id
        )

        return True

    def current_conversation(self) -> str:
        """
        Devuelve el ID de la conversación activa.
        """

        return self.conversation_id

    # ============================================================
    # PERSISTENCIA DE TURNOS
    # ============================================================

    def _save_user_message(self, message: str):
        """
        Guarda el mensaje del usuario en:

        1. ContextManager
        2. ConversationManager
        3. MemoryManager existente

        ContextManager ya delega la persistencia al
        ConversationManager, por lo que no se duplica SQLite.
        """

        self.context.add_message(
            "user",
            message,
            conversation_id=self.conversation_id,
        )

        # Compatibilidad con la memoria existente.
        try:
            self.memory.save_message(
                "user",
                message,
            )
        except Exception:
            pass

    def _save_assistant_message(self, message: str):
        """
        Guarda la respuesta de ARUS.
        """

        self.context.add_message(
            "assistant",
            message,
            conversation_id=self.conversation_id,
        )

        # Compatibilidad con MemoryManager.
        try:
            self.memory.save_message(
                "assistant",
                message,
            )
        except Exception:
            pass

    def _finish_response(self, response):
        """
        Normaliza una respuesta y la persiste.

        Devuelve AgentResponse para mantener compatibilidad con
        Controller y el resto del sistema.
        """

        if isinstance(response, AgentResponse):
            text = response.answer
            result = response
        else:
            text = str(response)

            result = AgentResponse(
                True,
                text
            )

        try:
            self._save_assistant_message(text)
        except Exception:
            pass

        return result

    # ============================================================
    # THINK
    # ============================================================

    def think(self, message):

        message = str(message).strip()

        if not message:
            return AgentResponse(
                True,
                "No he recibido ningún mensaje."
            )

        # --------------------------------------------------------
        # GUARDAR MENSAJE DEL USUARIO
        # --------------------------------------------------------

        try:
            self._save_user_message(message)
        except Exception as e:
            print("Conversation save error:", e)

        # --------------------------------------------------------
        # APRENDIZAJE
        # --------------------------------------------------------

        try:

            from learning.domain.knowledge import KnowledgeItem

            learning_manager.learn(
                KnowledgeItem(
                    title=message[:60],
                    content=message,
                    tags=["conversation"],
                )
            )

        except Exception as e:

            print("Learning error:", e)

        # --------------------------------------------------------
        # DETECTAR INTENCIÓN
        # --------------------------------------------------------

        try:

            intent = self.intent_detector.detect(
                message
            )

        except Exception:

            intent = None

        # --------------------------------------------------------
        # HERRAMIENTAS
        # --------------------------------------------------------

        if intent == "tool":

            from types import SimpleNamespace

            try:

                agent = ToolAgent()

                request = SimpleNamespace(
                    message=message
                )

                resultado = agent.execute(
                    request
                )

                return self._finish_response(
                    resultado
                )

            except Exception as e:

                return self._finish_response(
                    AgentResponse(
                        False,
                        "Herramienta no disponible: "
                        + str(e)
                    )
                )

        # --------------------------------------------------------
        # MEMORIA EXPLÍCITA
        # --------------------------------------------------------

        text = message.lower()

        if "mi nombre es" in text:

            nombre = (
                message.lower()
                .replace(
                    "mi nombre es",
                    ""
                )
                .strip()
            )

            self.memory.remember(
                "nombre",
                nombre
            )

            return self._finish_response(
                AgentResponse(
                    True,
                    f"Perfecto, recordaré que te llamas {nombre}."
                )
            )

        if (
            "como me llamo" in text
            or "cómo me llamo" in text
        ):

            nombre = self.memory.recall(
                "nombre"
            )

            if nombre:

                return self._finish_response(
                    AgentResponse(
                        True,
                        f"Te llamas {nombre}."
                    )
                )

        # --------------------------------------------------------
        # CONTEXTO REAL PARA EL MODELO
        # --------------------------------------------------------

        try:

            history = self.context.get_context(
                self.conversation_id
            )

        except Exception:

            # Fallback compatible con el sistema anterior.
            try:
                history = self.memory.history()
            except Exception:
                history = []

        # --------------------------------------------------------
        # MODELO IA
        # --------------------------------------------------------

        try:

            respuesta = self.model.generate(
                message,
                history,
            )

            return self._finish_response(
                AgentResponse(
                    True,
                    respuesta
                )
            )

        except Exception as e:

            print(
                "Model error:",
                e
            )

        # --------------------------------------------------------
        # ÚLTIMO RECURSO
        # --------------------------------------------------------

        return self._finish_response(
            AgentResponse(
                True,
                "Estoy aprendiendo todavía. "
                "¿Puedes explicarme mejor?"
            )
        )
