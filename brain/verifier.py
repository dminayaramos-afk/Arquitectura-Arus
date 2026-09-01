"""
ARUS
Verifier

Fase 7 del prompt maestro:

    PLAN -> EXECUTE -> VERIFY -> ¿Correcto?
                                    Sí -> RESPONSE
                                    No -> REPAIR / RETRY

No existía ningún Verifier en el proyecto (se auditó antes de escribir
esto: no hay coincidencias de "verif" en ningún módulo real). Esta es
infraestructura nueva, no la ampliación de algo que ya existiera.

Alcance deliberado: Verifier comprueba resultados ESTRUCTURADOS
(tareas de herramientas, respuestas de agentes) — cosas con un
"éxito/fallo" objetivo. Verificar una respuesta de texto libre del
modelo (chat normal) necesitaría razonamiento adicional (que el propio
modelo se autoevalúe), que no se finge aquí; se deja explícitamente
fuera de esta fase.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from brain.task import Task


@dataclass
class VerificationResult:

    ok: bool

    reason: str = ""

    subject: Any = None


class Verifier:

    def verify_task(self, task: Task) -> VerificationResult:
        """
        Verifica el resultado de una tarea (punto 15: herramientas,
        cálculos, tareas). Una tarea es correcta si terminó con
        estado 'done' y produjo un resultado no vacío.
        """

        if task.status == "error":
            return VerificationResult(
                False,
                f"La tarea '{task.name}' falló: {task.result}",
                task,
            )

        if task.status != "done":
            return VerificationResult(
                False,
                f"La tarea '{task.name}' no se completó (estado: {task.status}).",
                task,
            )

        if task.result is None or task.result == "":
            return VerificationResult(
                False,
                f"La tarea '{task.name}' terminó sin resultado.",
                task,
            )

        return VerificationResult(True, "", task)

    def verify_plan(self, tasks: list[Task]) -> tuple[bool, list[VerificationResult]]:

        resultados = [self.verify_task(t) for t in tasks]

        return all(r.ok for r in resultados), resultados

    def verify_agent_response(self, response: Any) -> VerificationResult:
        """
        Verifica una AgentResponse (o cualquier objeto con atributo
        `success`). Si el objeto no tiene `success`, se asume
        correcto (no todo lo que pasa por Brain es verificable de
        forma estructurada; ver docstring del módulo).
        """

        success = getattr(response, "success", None)

        if success is None:
            return VerificationResult(True, "", response)

        if not success:

            errores = getattr(response, "errors", None)

            razon = "; ".join(errores) if errores else str(
                getattr(response, "answer", response)
            )

            return VerificationResult(False, razon, response)

        return VerificationResult(True, "", response)

    def repair_task(self, task: Task, executor: Callable[[str, dict], Any]) -> VerificationResult:
        """
        REPAIR/RETRY (punto 15): reintenta una vez la ejecución de una
        tarea que falló la verificación. `executor` es la función que
        de verdad ejecuta la herramienta (p.ej. ToolManager.execute),
        para no duplicar aquí la lógica de ejecución de ninguna otra
        fase.
        """

        try:

            task.result = executor(task.name, **task.arguments)
            task.status = "done"

        except Exception as e:

            task.status = "error"
            task.result = f"Fallo tras reintento: {e}"

        return self.verify_task(task)

    def repair_agent(self, request: Any, retry: Callable[[Any], Any]) -> tuple[Any, VerificationResult]:
        """
        REPAIR/RETRY para respuestas de agentes: reintenta una vez la
        llamada `retry(request)` (p.ej. agent.execute) y devuelve la
        nueva respuesta junto con su verificación.
        """

        nueva_respuesta = retry(request)

        return nueva_respuesta, self.verify_agent_response(nueva_respuesta)
