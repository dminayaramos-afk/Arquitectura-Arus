"""
ARUS
Memory Manager

Punto central de acceso a toda la memoria del sistema.

Fase 5 añade los tres tipos de memoria de punto 6 del prompt maestro
que todavía faltaban (Semantic, Task, User Preferences), sobre la
misma base de datos que ya usa LongMemory (arus.db), sin crear
almacenes nuevos. Short-Term = working (WorkingMemory / ahora también
context.ContextManager desde Brain), Conversation Memory =
conversations.ConversationManager (Fase 2, no vive aquí para no
duplicar responsabilidad).

"summarize"/"classify"/"prioritize" (punto 6) necesitan razonamiento
real (un modelo), no solo almacenamiento — por eso no se fingen aquí;
MemoryManager expone las primitivas de búsqueda que Brain (que sí
tiene acceso al modelo desde la Fase 4) puede usar para construir
esas capacidades.
"""

from __future__ import annotations

from memory.working_memory import WorkingMemory
from memory.long_memory import LongMemory
from memory.persistent_memory import PersistentMemory
from memory.semantic_memory import SemanticMemory
from memory.user_preferences import UserPreferences
from memory.task_memory import TaskMemory, MemoryTask


class MemoryManager:
    """Gestiona todas las memorias de ARUS."""

    def __init__(self):

        self.working = WorkingMemory()

        self.long = LongMemory()

        self.persistent = PersistentMemory()

        self.semantic = SemanticMemory()

        self.preferences = UserPreferences()

        self.tasks = TaskMemory()


    def clear(self):

        self.working.clear()


    def history(self):

        return self.working.history()


    def remember(
        self,
        key,
        value,
    ):

        self.long.remember(
            key,
            value,
        )


    def recall(
        self,
        key,
    ):

        return self.long.recall(
            key,
        )


    def save_message(
        self,
        role,
        message,
    ):

        self.working.add(
            role,
            message,
        )

        self.persistent.save_message(
            role,
            message,
        )


    # --------------------------------------------------------
    # FASE 5 — SEMANTIC MEMORY
    # --------------------------------------------------------

    def remember_semantic(self, key, value, tags=None):
        self.semantic.add(
            key,
            value,
            tags=tags,
        )

    def recall_semantic(self, key):
        return self.semantic.get(key)

    # --------------------------------------------------------
    # FASE 5 — USER PREFERENCES
    # --------------------------------------------------------

    def set_preference(self, key, value):
        self.preferences.set(
            key,
            value,
        )

    def get_preference(self, key, default=None):
        return self.preferences.get(
            key,
            default,
        )

    # --------------------------------------------------------
    # FASE 5 — TASK MEMORY
    # --------------------------------------------------------

    def add_task(self, name, arguments=None):
        task = MemoryTask(
            name=name,
            arguments=arguments or {},
            status="pending",
            result=None,
        )

        self.tasks.save(
            name,
            {
                "arguments": task.arguments,
                "status": task.status,
                "result": task.result,
            },
        )

        return task

    def complete_task(self, task_id, result=None):
        state = self.tasks.get(task_id)

        if state is None:
            return None

        state["status"] = "done"
        state["result"] = result

        self.tasks.save(
            task_id,
            state,
        )

        return state

    def search(self, query: str) -> dict:
        """
        Busqueda unificada por palabra clave en Long-Term y Semantic
        Memory. No es RAG (Fase 8); es la base sobre la que la Fase 8
        podra construir busqueda semantica real.
        """

        return {
            "long": self.long.search(query),
            "semantic": self.semantic.search(query),
        }
