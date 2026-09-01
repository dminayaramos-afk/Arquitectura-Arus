# ARUS MARK 7 — FASE 2: ConversationManager

## Cómo instalar
Copia estas rutas dentro de tu proyecto ARUS (mismo nivel que `database/`, `brain/`, `memory/`):

- conversations/__init__.py
- conversations/conversation_manager.py
- database/conversation_session_repository.py   (archivo NUEVO, no sobrescribe nada)

No se ha tocado ningún archivo existente. `database/conversation_repository.py`
(la tabla `conversations` antigua, plana) se deja intacta.

## Qué hace
`ConversationManager` (paquete `conversations/`) añade dos tablas nuevas en tu
misma base de datos (`arus/data/arus.db`):

- `conversation_sessions`: id (uuid), title, created_at, updated_at, summary,
  metadata (JSON), favorite, archived.
- `conversation_messages`: cada turno de cada conversación, vinculado por
  conversation_id.

API disponible (para que la futura interfaz la consuma):

    create(title=None, metadata=None) -> conversation_id
    save(role, content, conversation_id=None)   # guardado incremental
    close(conversation_id=None)
    load(conversation_id) -> dict con messages
    resume(conversation_id) -> dict, y la deja como conversación activa
    recent(limit=20, include_archived=False)
    search(query)
    rename(conversation_id, title)
    delete(conversation_id)
    archive(conversation_id, archived=True)
    favorite(conversation_id, favorite=True)
    set_summary(conversation_id, summary)
    set_metadata(conversation_id, metadata)

`save()` se llama tras cada mensaje, no al cerrar — así no se pierde nada si
ARUS falla o se cierra de golpe (punto 3 del prompt maestro).

## Probado
Se ejecutó un test funcional end-to-end (crear, guardar 3 mensajes, cerrar,
reanudar, buscar, renombrar, marcar favorita, resumir, cargar, borrar) contra
la capa real de base de datos del proyecto. Resultado: correcto.

Compilación (`py_compile`) de los 3 archivos: sin errores.

## Lo que falta para integrarlo de verdad (pendiente, NO hecho todavía)
Esto es solo infraestructura. Para que se use en cada conversación real hace
falta conectar `ChatWidget → ARUSController` con `ConversationManager.save()`
en cada turno — eso es la Fase 4 del prompt maestro (unificar el cerebro y
corregir la ruta directa Chat→Ollama), y requiere antes localizar
exactamente dónde `arus/interface/chat.py` y `arus/interface/controller.py`
envían los mensajes hoy, para no romper la interfaz. No se ha hecho en esta
entrega.

## Estado de las 16 fases del prompt maestro
1. Auditoría — hecha en sesión anterior (limpieza de duplicados, ver
   fix_arus_v2.py)
2. ConversationManager — HECHO (esta entrega)
3. ContextManager — NO IMPLEMENTADO
4. Unificar Chat→Controller→Brain→ModelManager — NO IMPLEMENTADO
5. Mejorar MemoryManager (short/long/semantic/task/preferences) — NO IMPLEMENTADO
6. Planner + Tools + Agents integrados en un ciclo — NO IMPLEMENTADO
7. Verifier — NO IMPLEMENTADO
8. RAG + documentos + proyectos — NO IMPLEMENTADO
9. Git/GitHub — NO IMPLEMENTADO
10. Código (asistente de programación) — NO IMPLEMENTADO
11. Voz (JARVIS-like, streaming, interrumpible) — NO IMPLEMENTADO
12. Visión — NO IMPLEMENTADO
13. Tareas autónomas (TaskManager) — ya existe brain/task_manager.py, sin
    revisar a fondo
14. Seguridad (PermissionManager/AuditLogger/Sandbox) — NO IMPLEMENTADO
15. Plugins — NO IMPLEMENTADO
16. Evaluación automática — NO IMPLEMENTADO

Hardware/CapabilityManager/ResourceManager (puntos 67-95 del prompt) — NO
IMPLEMENTADO.
