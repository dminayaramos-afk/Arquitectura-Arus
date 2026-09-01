# ARUS MARK 7 — FASE 5: Memoria (multinivel) + integración con Brain

## Como instalar
Sustituye/añade estos archivos en tu proyecto (mismas rutas):

    memory/long_memory.py        (modificado)
    memory/memory_manager.py     (modificado)
    memory/semantic_memory.py    (nuevo)
    memory/task_memory.py        (nuevo)
    memory/user_preferences.py   (nuevo)
    database/memory_repository.py (nuevo)
    brain/brain.py               (modificado)

Requiere Fase 2 (`conversations/`) y Fase 3 (`context/context_manager.py`
ampliado) ya instaladas — Brain las usa directamente ahora.

No se toco `arus/interface/*` en esta fase (verificado byte a byte:
main_window.py, controller.py, core_visual.py identicos al original).

## Que se hizo

### 1. Los 6 tipos de memoria del punto 6 del prompt maestro
- **Short-Term**: `WorkingMemory` (ya existia) + ahora tambien
  `ContextManager` desde Brain (Fase 3).
- **Conversation Memory**: `ConversationManager` (Fase 2) — no vive en
  `memory/` para no duplicar responsabilidad.
- **Long-Term Memory**: `LongMemory`. Antes era un diccionario en RAM
  que se perdia al cerrar ARUS (contradecia su proposito). Ahora
  persiste en SQLite.
- **Semantic Memory**: `SemanticMemory` (nuevo). Busqueda por palabra
  clave sobre lo que se le "enseña" a ARUS. No es RAG real — eso es
  Fase 8 (embeddings/vector store); esto es la base minima sobre la
  que la Fase 8 podra construir sin cambiar la API.
- **Task Memory**: `TaskMemory` (nuevo). Guarda el *estado* de tareas
  para que sobreviva a un reinicio. No sustituye a
  `brain/task_manager.py` (que gestiona la ejecucion en curso, en
  RAM); conectar ambos es trabajo de la Fase 13 (tareas autonomas).
- **User Preferences**: `UserPreferences` (nuevo). Preferencias
  explicitas (idioma, formato, etc.), separadas de Long Memory porque
  son datos de naturaleza distinta.

### 2. Una sola tabla nueva, no cinco
`Semantic`, `Task` y `UserPreferences` (y `Long`) comparten
`database/memory_repository.py` — una tabla `memory_entries` con
columna `namespace` para separarlos, en vez de crear una tabla SQLite
por tipo de memoria. Evita duplicar esquema.

Nota: el proyecto ya tenia `database/knowledge_repository.py` y
`database/settings_repository.py` como esqueletos (solo
`create_table()`, sin nada que los usara). Se dejaron tal cual
estaban — no se les añadio CRUD porque `MemoryRepository` los
sustituye funcionalmente sin duplicar tablas.

### 3. Brain ya NO usa memoria muerta
Hallazgo real: `self.memory.history()` en `brain.think()` SIEMPRE
devolvia una lista vacia, porque nada en el proyecto llamaba a
`MemoryManager.save_message()`. El modelo recibia el historial vacio
en cada turno, aunque hubiera codigo de "memoria de conversacion".

Ahora `Brain.__init__` crea su propio `ConversationManager` +
`ContextManager` (una conversacion de sesion se abre automaticamente
al arrancar), y `think()`:
- usa `self.context.get_context(self.conversation_id)` como historial
  real para `ModelManager.generate()`;
- persiste cada turno (usuario + respuesta) via
  `self._remember_turn()`, un unico punto de guardado para no
  duplicar mensajes en dos tablas.

Se añadio `Brain.resume_conversation(conversation_id)` para que la
futura interfaz de "conversaciones recientes" (punto 2) pueda
retomarlas.

La tabla plana antigua (`ConversationRepository` / `save_message` de
`MemoryManager`) se deja sin usar pero SIN BORRAR, tal como pide la
regla de no eliminar funcionalidad existente.

### 4. Lo que "summarize / classify / prioritize" (punto 6) necesitan
Esas tres capacidades necesitan razonamiento real (un modelo), no
solo almacenamiento — por eso no se fingen aqui. `MemoryManager`
expone las primitivas de busqueda (`search()`) que `Brain`, que ya
tiene acceso al modelo desde la Fase 4, podra usar para construirlas
de verdad mas adelante.

## Observacion menor (no es un bug de esta fase)
`brain.think()` ya guardaba el nombre en minusculas
(`message.lower()...`) antes de esta fase — "Mi nombre es Danny" se
recuerda como "danny". Es un comportamiento preexistente que no se
toco; si quieres que respete mayusculas, dimelo y lo ajusto en una
fase aparte.

## Probado (con stubs de PySide6/ollama, no instalados en mi entorno)
1. `LongMemory` sobrevive a "reiniciar ARUS" (nueva instancia, misma
   DB): OK.
2. `UserPreferences` persiste y tiene valor por defecto: OK.
3. `TaskMemory.pending()` filtra correctamente por estado: OK.
4. `SemanticMemory.search()` encuentra por palabra clave: OK.
5. `MemoryManager` expone los 6 tipos juntos y funcionan: OK.
6. `Brain.think()` usa el contexto real (no vacio), el system prompt
   de identidad sigue llegando a Ollama, y ambos turnos quedan
   persistidos via `ConversationManager`: OK.
7. La memoria de "mi nombre es / como me llamo" sigue funcionando
   dentro de `Brain.think()`: OK.
8. `resume_conversation()` cambia de conversacion activa
   correctamente: OK.
9. Fases 2/3/4 sin regresion: interfaz identica byte a byte, sintaxis
   de todo el proyecto (`py_compile`) sin errores.

## FASE 5 — RESULTADO

Archivos creados:
- database/memory_repository.py
- memory/semantic_memory.py
- memory/task_memory.py
- memory/user_preferences.py

Archivos modificados:
- memory/long_memory.py (ahora persiste; misma API publica)
- memory/memory_manager.py (expone semantic/preferences/tasks)
- brain/brain.py (usa ConversationManager+ContextManager reales en
  vez de WorkingMemory muerto; nuevo metodo resume_conversation)

Archivos NO modificados:
- database/knowledge_repository.py, database/settings_repository.py
  (se dejaron como esqueletos originales; superados por
  memory_repository.py)
- arus/interface/* (verificado identico byte a byte)
- conversations/*, context/context_window.py, context_builder.py,
  context_formatter.py, context_retriever.py

Pruebas:
- Persistencia (Long/Preferences/Task/Semantic): OK
- Integracion Brain <-> Conversation/Context: OK
- Identidad ARUS preservada: OK
- Memoria de nombre: OK
- Sintaxis global del proyecto: OK
- Interfaz visual: sin cambios
- Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
  entorno (paquetes no instalados aqui) — confirmalo en tu maquina.

Pendiente para siguientes fases: Planner + Tools + Agents integrados
en un ciclo unico (Fase 6), Verifier (Fase 7), y de ahi en adelante
RAG, Git, codigo, voz, vision, tareas autonomas, seguridad, plugins y
evaluacion (Fases 8-16).
