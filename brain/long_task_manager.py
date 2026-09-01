"""
ARUS
Long Task Manager (Fase 13, punto 33 del prompt maestro)

No confundir con `brain.task_manager.TaskManager` (Fase 6/7): ese
gestiona la resolución de UNA llamada a herramientas dentro de una
sola respuesta del modelo (vive y muere en una llamada a
`generate()`, en RAM). Esto es distinto: tareas LARGAS y visibles
para el usuario, con varios pasos, que deben sobrevivir a que ARUS se
cierre o se reinicie -- exactamente el ejemplo del punto 33:

    TASK #001
    ✓ Analizar proyecto
    ✓ Analizar dependencias
    ✓ Analizar memoria
    → Analizando herramientas
    ○ Analizar voz
    ○ Generar informe

`LongTaskManager` es un rastreador de progreso persistente (crear,
pausar, continuar, cancelar, consultar estado, guardar progreso,
recuperar tras reinicio) -- NO ejecuta los pasos por su cuenta. Quien
hace el trabajo real de cada paso (Brain, un agente, una herramienta)
llama a `advance()` cuando termina un paso. Separar "quién ejecuta" de
"quién lleva la cuenta" es intencional: así esta clase no duplica ni
Planner ni TaskManager ni ningún agente.

Se apoya en `database.memory_repository.MemoryRepository` (Fase 5),
el mismo almacén clave-valor con namespace que usa el resto de la
memoria -- namespace propio ("long_tasks") para no mezclarse con
nada más.

NOTA (ARUS MARK 9): originalmente esto se apoyaba en
`memory.task_memory.TaskMemory`, pero se detectó que esa clase fue
rediseñada para otro propósito -- ahora envuelve cada entrada en un
objeto `MemoryTask` (con solo `name/arguments/status/result`, sin
soporte de asignación tipo diccionario) pensado para el estado de
tareas cortas de herramientas que ya usa `MemoryManager`
(`memory_manager.py` construye `MemoryTask` directamente). Usar esa
misma clase aquí rompía `LongTaskManager` en cuanto se llamaba a
`start()` (`TypeError: 'MemoryTask' object does not support item
assignment`), porque la estructura multi-paso de una tarea larga
(title, current_step, steps) no cabe en ese objeto. En vez de romper
`TaskMemory` para el otro caso de uso que ya la necesita tal como
está, `LongTaskManager` pasó a hablar directamente con
`MemoryRepository` (la capa de persistencia real que hay debajo de
ambas), con su propio namespace.
"""

from __future__ import annotations

import uuid
from typing import Optional

from database.database import Database
from database.memory_repository import MemoryRepository

_NAMESPACE = "long_tasks"

ESTADOS_TERMINALES = {"done", "cancelled", "error"}


class LongTaskManager:

    def __init__(self, database: Database = None):

        self.database = database or Database()

        self.repo = MemoryRepository(self.database)

        self.repo.create_table()

    def create(self, title: str, steps: list[str]) -> str:

        if not steps:
            raise ValueError("Una tarea larga necesita al menos un paso.")

        task_id = str(uuid.uuid4())

        estado = {
            "id": task_id,
            "title": title,
            "status": "pending",
            "current_step": 0,
            "steps": [
                {"name": nombre, "status": "pending", "result": None}
                for nombre in steps
            ],
        }

        self.repo.set(_NAMESPACE, task_id, estado)

        return task_id

    def get(self, task_id: str) -> Optional[dict]:

        return self.repo.get(_NAMESPACE, task_id)

    def start(self, task_id: str):

        tarea = self._requerir(task_id)

        tarea["status"] = "running"

        self.repo.set(_NAMESPACE, task_id, tarea)

        return tarea

    def advance(self, task_id: str, result=None):
        """Marca el paso actual como hecho y avanza al siguiente."""

        tarea = self._requerir(task_id)

        if tarea["status"] == "paused":
            raise ValueError("No se puede avanzar una tarea pausada; reanúdala primero con resume().")

        if tarea["status"] in ESTADOS_TERMINALES:
            raise ValueError(f"La tarea ya está en estado final ('{tarea['status']}').")

        pasos = tarea["steps"]

        indice = tarea["current_step"]

        if indice >= len(pasos):
            return tarea

        pasos[indice]["status"] = "done"
        pasos[indice]["result"] = result

        siguiente = indice + 1

        tarea["current_step"] = siguiente

        if siguiente >= len(pasos):
            tarea["status"] = "done"
        else:
            tarea["status"] = "running"

        self.repo.set(_NAMESPACE, task_id, tarea)

        return tarea

    def fail_step(self, task_id: str, error: str):

        tarea = self._requerir(task_id)

        pasos = tarea["steps"]

        indice = tarea["current_step"]

        if indice < len(pasos):
            pasos[indice]["status"] = "error"
            pasos[indice]["result"] = error

        tarea["status"] = "error"

        self.repo.set(_NAMESPACE, task_id, tarea)

        return tarea

    def pause(self, task_id: str):

        tarea = self._requerir(task_id)

        if tarea["status"] in ESTADOS_TERMINALES:
            raise ValueError(f"No se puede pausar una tarea en estado '{tarea['status']}'.")

        tarea["status"] = "paused"

        self.repo.set(_NAMESPACE, task_id, tarea)

        return tarea

    def resume(self, task_id: str):

        tarea = self._requerir(task_id)

        if tarea["status"] != "paused":
            raise ValueError(f"Solo se puede reanudar una tarea pausada (estado actual: '{tarea['status']}').")

        tarea["status"] = "running"

        self.repo.set(_NAMESPACE, task_id, tarea)

        return tarea

    def cancel(self, task_id: str):

        tarea = self._requerir(task_id)

        if tarea["status"] in ESTADOS_TERMINALES:
            raise ValueError(f"La tarea ya está en estado final ('{tarea['status']}').")

        tarea["status"] = "cancelled"

        self.repo.set(_NAMESPACE, task_id, tarea)

        return tarea

    def active(self) -> list[dict]:
        """Tareas recuperables tras un reinicio (no en estado final)."""

        return [
            estado
            for estado in self.repo.all(_NAMESPACE).values()
            if estado.get("status") not in ESTADOS_TERMINALES
        ]

    def progress_text(self, task_id: str) -> str:
        """
        Formato de progreso legible, como el ejemplo del punto 33.
        No es para la interfaz (que no se toca) -- es para que Brain
        pueda contarle a Danny en qué va una tarea larga por chat.
        """

        tarea = self._requerir(task_id)

        simbolos = {"done": "✓", "error": "✗", "pending": "○"}

        lineas = [f"TAREA: {tarea['title']} ({tarea['status']})"]

        for i, paso in enumerate(tarea["steps"]):

            if i == tarea["current_step"] and tarea["status"] == "running":
                marca = "→"
            else:
                marca = simbolos.get(paso["status"], "○")

            lineas.append(f"{marca} {paso['name']}")

        return "\n".join(lineas)

    def _requerir(self, task_id: str) -> dict:

        tarea = self.repo.get(_NAMESPACE, task_id)

        if tarea is None:
            raise KeyError(f"No existe la tarea: {task_id}")

        return tarea
