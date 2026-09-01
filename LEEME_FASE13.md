# ARUS MARK 7 — FASE 13: Tareas autónomas

## Como instalar
Añade/sustituye (mismas rutas):

    brain/long_task_manager.py   (nuevo)
    brain/brain.py               (modificado: expone self.long_tasks)

No se toco `arus/interface/*` ni `brain/task_manager.py` (el que ya
usan las Fases 6-7).

## Auditoria previa: no se duplica nada
`brain/task_manager.py` YA existe, pero gestiona algo distinto: la
resolucion de UNA llamada a herramientas dentro de una sola respuesta
del modelo (vive y muere en RAM en una llamada a `generate()`, Fase
6/7). El punto 33 pide otra cosa: tareas LARGAS, visibles para el
usuario, con progreso persistente que sobreviva a un reinicio -- eso
no existia. Se creo `LongTaskManager` como una clase nueva y
distinta, sin tocar `task_manager.py`.

Se apoya en `memory/task_memory.py` (Fase 5), que en su propio
docstring ya decia "conectar esto es trabajo de la Fase 13" -- se
revive codigo que ya estaba preparado para esto, no se inventa
almacenamiento nuevo.

## Diseño: quien lleva la cuenta no es quien ejecuta
`LongTaskManager` NO ejecuta los pasos por su cuenta -- solo crea,
seguimiento de progreso, pausa, reanuda, cancela y persiste. Quien
hace el trabajo real de cada paso (Brain, un agente, una herramienta)
llama a `advance(task_id, result=...)` cuando termina un paso. Asi no
duplica ni Planner ni TaskManager ni ningun agente; es la "memoria de
progreso" de una tarea larga, no otro motor de ejecucion.

## API (punto 33)
    create(title, steps: list[str]) -> task_id
    start(task_id)
    advance(task_id, result=None)     -> marca el paso actual como hecho, avanza
    fail_step(task_id, error)
    pause(task_id)
    resume(task_id)
    cancel(task_id)
    get(task_id) -> dict completo
    active()                           -> tareas recuperables tras reinicio
    progress_text(task_id)             -> formato legible, igual al
                                           ejemplo del punto 33

## Bug real que encontre probandolo (no en la primera version)
Mi primer `advance()` no comprobaba el estado de la tarea -- se podia
"avanzar" una tarea pausada sin querer, y quedaba en 'running' sin que
nadie la hubiera reanudado explicitamente. Lo detecte al escribir el
test de pausar/reanudar (el `resume()` fallaba porque la tarea ya
estaba en 'running', no en 'paused', por culpa de ese avance
silencioso) y lo arregle: `advance()` ahora rechaza avanzar una tarea
pausada o ya terminada, con un error claro.

## Probado
1. Crear una tarea con 6 pasos (el mismo ejemplo del punto 33).
2. Avanzar varios pasos y comprobar que `progress_text()` produce
   exactamente el formato ✓/→/○ del prompt maestro.
3. Pausar de verdad bloquea `advance()` (aqui encontre y arregle el
   bug de arriba); reanudar lo permite de nuevo.
4. **La prueba central de la fase:** avanzar hasta el paso 4, borrar
   el `LongTaskManager` de Python (simulando cerrar ARUS), crear uno
   nuevo (simulando reiniciarlo), y comprobar que la tarea sigue ahi
   con el progreso EXACTO donde se quedo. Funciono.
5. Completar el resto de pasos hasta `status == 'done'`.
6. Cancelar una tarea.
7. `fail_step()` marca el paso y la tarea en error, con el motivo.
8. `active()` excluye correctamente las tareas ya terminadas
   (done/cancelled/error) -- para un futuro panel de la interfaz que
   solo muestre lo que sigue en curso.
9. IDs invalidos dan errores claros, no crashes silenciosos.
10. `Brain` expone `self.long_tasks` funcional, sin romper nada.
11. Sin regresion en Fases 2-12. Interfaz identica byte a byte.
    Sintaxis de todo el proyecto: OK.

## FASE 13 — RESULTADO

Archivos creados:
- brain/long_task_manager.py

Archivos modificados:
- brain/brain.py (expone self.long_tasks)

Archivos NO modificados:
- arus/interface/*, brain/task_manager.py, memory/task_memory.py

Pruebas: 11 casos reales, incluyendo simular un reinicio completo de
ARUS a mitad de una tarea larga. Interfaz visual: sin cambios.
Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
entorno — confirmalo en tu maquina.

Pendiente: decidir cuando Brain abre una tarea larga automaticamente
en vez de responder directo (p.ej. "analiza todo mi proyecto" podria
crear una LongTaskManager task con los pasos del punto 24); Fase 14
(Seguridad) en adelante hasta Fase 16; decisiones pendientes de fases
anteriores (agentes duplicados, RAG, confirmacion Git, STT duplicado,
voz->Brain->voz, entrada de imagen en la interfaz).
