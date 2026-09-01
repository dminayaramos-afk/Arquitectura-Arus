"""
ARUS
Brain
"""

from __future__ import annotations
from agents.agent_response import AgentResponse

from ai.model_manager import ModelManager
from memory.memory_manager import MemoryManager
from tools.tool_manager import ToolManager
from brain.task_manager import TaskManager
from brain.planner import Planner
from security.permission_manager import PermissionManager
from security.audit_logger import AuditLogger
from security.rate_limiter import RateLimiter

from brain.intent_detector import IntentDetector
from brain.verifier import Verifier
from agents.agent_request import AgentRequest
from agents.agent_registry import AgentRegistry
from agents.agent_router import AgentRouter
from agents.tool_agent import ToolAgent
from learning import learning_manager

from conversations.conversation_manager import ConversationManager
from context.context_manager import ContextManager
from rag.rag_manager import RAGManager
from vision.vision_manager import VisionManager
from brain.long_task_manager import LongTaskManager


class Brain:

    def __init__(self):

        self.model = ModelManager()
        self.memory = MemoryManager()
        self.tools = ToolManager()
        self.tasks = TaskManager()
        self.planner = Planner()
        self.verifier = Verifier()
        self.permissions = PermissionManager()
        self.audit = AuditLogger()
        self.rate = RateLimiter()

        # Fase 5: conversación real (persistida) + contexto acotado
        # que se le entrega al modelo, en vez del WorkingMemory en
        # RAM que nunca llegaba a guardarse (self.memory.history()
        # siempre estaba vacío porque nada llamaba a save_message).
        # Brain abre una conversación por sesión; cuando exista un
        # selector de conversaciones en la interfaz (punto 2), podrá
        # llamar a self.resume_conversation(id) para retomar otra.
        self.conversation_manager = ConversationManager()
        self.context = ContextManager(conversation_manager=self.conversation_manager)
        self.conversation_id = self.conversation_manager.create(title="Sesión ARUS")

        # Fase 8: RAG disponible como capacidad (self.rag.query(...),
        # self.rag.index_project(...)) pero deliberadamente NO
        # conectado todavía a think() -- ver docstring de
        # rag/rag_manager.py sobre por qué esa decisión se deja fuera
        # de esta fase.
        self.rag = RAGManager()

        # Fase 12: visión disponible como capacidad (self.vision.analyze(...))
        # pero, igual que self.rag, no conectada al flujo automático de
        # think() -- y aquí ni siquiera hay por dónde entraría una
        # imagen desde la interfaz actual (ver docstring de
        # vision/vision_manager.py).
        self.vision = VisionManager()

        # Fase 13: tareas largas persistentes, disponibles como
        # capacidad (self.long_tasks.create(...)/advance(...)/...)
        # pero, igual que self.rag y self.vision, no conectadas
        # todavía a ningún disparador automático en think() -- decidir
        # cuándo Brain abre una tarea larga en vez de responder
        # directamente es una decisión de producto que se deja fuera
        # de esta fase.
        self.long_tasks = LongTaskManager()

        # Intent Detector
        self.intent_detector = IntentDetector()

        # Agentes
        self.registry = AgentRegistry()
        self.registry.register(
            "tool",
            ToolAgent(),
        )

        self.router = AgentRouter(
            self.registry
        )


    def resume_conversation(self, conversation_id: str):
        """
        Retoma una conversación persistida (Fase 2) en lugar de la
        sesión actual. Pensado para que la futura interfaz de
        "conversaciones recientes" (punto 2) pueda llamarlo.
        """

        self.context.resume(conversation_id)
        self.conversation_id = conversation_id


    def think(self, message):

        

        # Detectar intención usando el sistema oficial
        intent = self.intent_detector.detect(message)

        

        # Guardar conversación en aprendizaje
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


        # Herramientas
        if intent == "tool":

            from agents.tool_agent import ToolAgent
            from types import SimpleNamespace

            try:
                agent = ToolAgent()

                request = SimpleNamespace(
                    message=message
                )

                resultado = agent.execute(request)

                # Fase 7: VERIFY -> ¿correcto? -> REPAIR/RETRY si no.
                # Antes, lo que devolviera el agente (éxito o fallo)
                # se aceptaba tal cual, sin comprobarlo ni reintentar.
                verificacion = self.verifier.verify_agent_response(resultado)

                if not verificacion.ok:
                    resultado, verificacion = self.verifier.repair_agent(
                        request, agent.execute
                    )

                self._remember_turn(message, str(resultado))

                return resultado

            except Exception as e:

                return AgentResponse(
                    False,
                    "Herramienta no disponible: " + str(e)
                )



        # Memoria simple
        text = message.lower()

        if "mi nombre es" in text:

            nombre = message.lower().replace(
                "mi nombre es",
                ""
            ).strip()

            self.memory.remember(
                "nombre",
                nombre
            )

            respuesta_nombre = f"Perfecto, recordaré que te llamas {nombre}."

            self._remember_turn(message, respuesta_nombre)

            return AgentResponse(
                True,
                respuesta_nombre
            )


        if "como me llamo" in text or "cómo me llamo" in text:

            nombre = self.memory.recall(
                "nombre"
            )

            if nombre:

                respuesta_nombre = f"Te llamas {nombre}."

                self._remember_turn(message, respuesta_nombre)

                return AgentResponse(
                    True,
                    respuesta_nombre
                )


        # Chat IA
        try:

            historial = self.context.get_context(self.conversation_id)

            # Capa 4 (ARUS MARK 9): Brain -> SkillManager.
            # `self.skills` lo inyecta ARUSController tras crear Brain
            # (brain.skills = skills) -- no todo el mundo que
            # instancia Brain() directamente pasa por el controller
            # (p.ej. los tests), así que se comprueba con getattr en
            # vez de asumir que existe.
            #
            # Solo se usa para intent == "ai": AIChatSkill ya envuelve
            # ModelManager exactamente igual que esta rama, así que
            # usarla es una conexión real sin cambiar el resultado.
            # NO se usa para intent == "chat": esa skill (ChatSkill)
            # es un stub que solo hace "Has dicho: " + message -- 
            # conectarla aquí habría roto los saludos normales
            # (auditado antes de tocar nada; se deja tal cual, no es
            # el alcance de esta tarea rediseñar esa skill).
            skills = getattr(self, "skills", None)

            if skills is not None and intent == "ai":

                respuesta = skills.execute(intent, message, historial)

            else:

                respuesta = self.model.generate(
                    message,
                    historial
                )

            self._remember_turn(message, respuesta)

            return AgentResponse(
                True,
                respuesta
            )

        except Exception as e:

            print("Model error:", e)

            # ARUS MARK 9, punto 4: "no ocultes errores reales". Antes
            # este fallo (típicamente Ollama no está corriendo) caía
            # siempre en el mensaje genérico de más abajo
            # ("Estoy aprendiendo todavía..."), indistinguible de que
            # el modelo simplemente no entendió el mensaje. Ahora se
            # informa con claridad de que el problema es de conexión
            # con el proveedor de IA -- el resto de ARUS (memoria,
            # comandos, herramientas) sigue funcionando con normalidad,
            # solo falla la generación de texto libre.
            mensaje_error = (
                "No puedo generar una respuesta ahora mismo: no logro "
                "conectar con el proveedor de IA (¿está Ollama en "
                "marcha?). El resto de ARUS (memoria, comandos, "
                "herramientas) sigue funcionando con normalidad."
            )

            self._remember_turn(message, mensaje_error)

            return AgentResponse(
                False,
                mensaje_error,
            )


        # Último recurso
        respuesta_defecto = "Estoy aprendiendo todavía. ¿Puedes explicarme mejor?"

        self._remember_turn(message, respuesta_defecto)

        return AgentResponse(
            True,
            respuesta_defecto
        )


    def _remember_turn(self, user_message: str, assistant_message: str):
        """
        Persiste el turno en la conversación actual (Fase 2/3). Un
        solo punto de guardado para no duplicar mensajes en dos
        tablas distintas (se reemplaza el guardado a la tabla plana
        antigua de MemoryManager.save_message, que se deja sin usar
        pero sin borrar).
        """

        try:
            self.context.add_message("user", user_message, self.conversation_id)
            self.context.add_message("assistant", str(assistant_message), self.conversation_id)
        except Exception as e:
            print("No se pudo persistir el turno de conversación:", e)

