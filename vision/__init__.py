"""
ARUS - Vision (Fase 12, punto 26 del prompt maestro)

IMAGE -> VISION MODEL -> ANALYSIS -> BRAIN

No existía nada real de esto en el proyecto: `arus/laboratory/` tiene
un par de Enum (`FileType.IMAGE`, `MediaType.IMAGE`) pero es código
sin usar (solo lo referencian sus propios tests y el script de
limpieza de la Fase 1) — no hay carga de imágenes, ni provider, ni
nada que hable con un modelo de visión. Infraestructura nueva, igual
que RAG (Fase 8) y Verifier (Fase 7).

Igual que con RAG y con la voz: no se finge disponibilidad. Si no hay
un modelo de visión real accesible en Ollama, `VisionManager` lo dice
honestamente en vez de simular que "ve" algo.
"""

from vision.vision_manager import VisionManager

__all__ = ["VisionManager"]
