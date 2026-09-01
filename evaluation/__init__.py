"""
ARUS - Evaluación automática (Fase 16, punto 50 del prompt maestro)

Batería de pruebas para ejecutar antes y después de cambios
importantes, cubriendo: Contexto, Memoria, Conversación larga,
Herramientas, Código, Web, RAG, Archivos, Voz, Errores, Seguridad,
Tareas, Agentes.

No existía nada de esto en el proyecto (auditado antes de escribir).
"""

from evaluation.suite import run_all

__all__ = ["run_all"]
