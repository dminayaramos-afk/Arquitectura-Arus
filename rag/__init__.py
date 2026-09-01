"""
ARUS - RAG (Fase 8)

Documents -> Parser -> Chunking -> Embeddings -> Vector Store ->
Retriever -> Brain (punto 23 del prompt maestro).

No existía nada de esto en el proyecto (auditado antes de escribir:
sin coincidencias reales de "rag"/"embedding"/"vector"/"chunk" salvo
comentarios propios de fases anteriores que ya apuntaban aquí).

Decisión de diseño explícita: embeddings ligeros por hashing (sin
librerías de ML ni descargas de modelos), consistente con la filosofía
de adaptación a hardware limitado del prompt maestro (puntos 67-95,
que todavía no están implementados como CapabilityManager, pero cuyo
criterio ya se puede aplicar aquí: no asumir que hay GPU/mucha RAM/
internet disponibles). Cuando exista CapabilityManager, podrá
sustituir `rag.embeddings.Embeddings` por un proveedor más pesado sin
tocar el resto del paquete.
"""

from rag.rag_manager import RAGManager

__all__ = ["RAGManager"]
