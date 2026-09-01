# ARUS MARK 7 — FASE 3: ContextManager

## Hallazgo importante antes de implementar
Tu proyecto YA tenia un `context/` parcial (context_manager.py,
context_window.py, context_builder.py, context_formatter.py,
context_retriever.py). No estaba conectado a nada (ningun otro
archivo del proyecto lo importaba — igual que
`MemoryManager.save_message()`, que tampoco se llama desde ningun
sitio hoy).

Por eso NO cree una arquitectura paralela: **amplie el
`context/context_manager.py` que ya existia**, sin tocar
`context_window.py`, `context_builder.py`, `context_formatter.py` ni
`context_retriever.py`.

## Como instalar
Sustituye tu `context/context_manager.py` por el de esta entrega
(es el mismo archivo, ampliado — no un modulo nuevo). En Windows
(PowerShell) o Linux, desde la raiz del proyecto:

    Copy-Item context_manager.py context/context_manager.py -Force   # Windows
    cp context_manager.py context/context_manager.py                # Linux/Mac

Copia tambien `context_tests/test_fase3_context_manager.py` a tu
proyecto (carpeta `context_tests/`) y ejecuta:

    python context_tests/test_fase3_context_manager.py

Requiere que la Fase 2 (`conversations/`) ya este instalada.

## Que cambio exactamente en context_manager.py
La API original se mantiene igual (no rompe nada que ya la use):

    add_user_message(message)
    add_assistant_message(message)
    get_context()
    clear()

Se añadio (opcional, con valores por defecto que no cambian el
comportamiento anterior):

    ContextManager(max_messages=20, max_chars=12000,
                    conversation_manager=None, summarizer=None)

    add_message(role, content, conversation_id=None)
    resume(conversation_id, limit=None)
    needs_compaction(conversation_id=None)
    compact(conversation_id=None)
    to_prompt(conversation_id=None)   # reusa ContextBuilder, no duplica formateo

## Responsabilidad de ContextManager vs ConversationManager
- ConversationManager (Fase 2): persistencia — crea, guarda, busca,
  archiva conversaciones completas en SQLite.
- ContextManager (Fase 3): la ventana de mensajes recientes que se le
  entregaria al modelo para UNA conversacion, con limite de mensajes
  y de caracteres. Cuando se le conecta un ConversationManager,
  ContextManager persiste ahi cada turno (no duplica el
  almacenamiento) y puede reconstruir el contexto de una conversacion
  antigua con `resume()`.

## Compactacion (punto 9 del prompt maestro)
Cuando el contexto crece demasiado, `compact()` recorta la ventana en
memoria (la persistencia en SQLite queda intacta e integra) y guarda
un resumen via `conversation_manager.set_summary()`. Sin resumen por
IA todavia (eso es Fase 4/Brain), usa un resumen de emergencia
honesto: cuenta de turnos + primer y ultimo mensaje. El parametro
`summarizer` permite que Brain, en la Fase 4, inyecte un resumen real
generado por el modelo sin tocar este archivo otra vez.

## Lo que NO se hizo (pendiente para Fase 4)
- No se conecto ChatWidget/ARUSController/Brain con ContextManager.
- No se toco `brain.py` (se verifico byte a byte: identico al
  original).
- No se toco `memory_manager.py`.
- No se reemplazo `self.memory.history()` en `brain.think()` por
  `ContextManager`. Sigue usando `WorkingMemory` como hasta ahora.
- No se implemento resolucion de referencias ("eso", "hazlo") —
  necesita el modelo, corresponde a Brain en Fase 4; ContextManager
  solo deja preparado el contexto sobre el que esa resolucion
  podra operar despues.
- `ContextRetriever` (memoria semantica por palabra clave) se dejo
  sin tocar; integrarlo en el contexto final tambien es Fase 4.

## FASE 3 — RESULTADO

Archivos creados:
- context_tests/test_fase3_context_manager.py

Archivos modificados:
- context/context_manager.py (ampliado; API original intacta)

Archivos NO modificados:
- context/context_window.py
- context/context_builder.py
- context/context_formatter.py
- context/context_retriever.py
- brain/brain.py (verificado identico byte a byte)
- memory/memory_manager.py (verificado identico byte a byte)
- arus/interface/* (no tocado)
- conversations/* (Fase 2, no tocado)

Pruebas (10 casos, todos ejecutados de verdad, no pseudocodigo):
- ContextManager: OK (crear, anadir, recuperar, orden, vacio, limites,
  conversacion larga, errores controlados)
- ConversationManager: OK (no se rompio; conversaciones independientes
  A/B verificadas)
- Persistencia: OK (contexto recortado en memoria vs. historial
  completo integro en SQLite, verificado)
- Imports: OK
- Sintaxis (py_compile de los 5 archivos de context/ + Fase 2): OK
- Arranque ARUS: NO VERIFICABLE en este entorno — falta el paquete
  `ollama` (dependencia externa, sin conexion a internet en el
  entorno donde desarrolle esto). brain.py no fue tocado, asi que el
  arranque deberia comportarse igual que antes de esta fase; te
  recomiendo confirmarlo tu en tu maquina real tras instalar el
  archivo.

Responsabilidad actual de ContextManager: preparar y limitar, por
conversacion, los mensajes que se entregarian al modelo, delegando la
persistencia real en ConversationManager y dejando un punto de
extension (`summarizer`) para cuando Brain pueda generar resumenes
con IA.

Relacion con ConversationManager: ContextManager es un consumidor
opcional de ConversationManager (se le pasa por constructor); nunca
al reves. Ninguno de los dos duplica la base de datos del otro.

Pendiente para Fase 4: conectar `arus/interface/chat.py` ->
`ARUSController` -> `Brain` para que `brain.think()` use
`ContextManager`/`ConversationManager` en lugar de (o ademas de)
`WorkingMemory`, y cortar la llamada directa a Ollama si existiera en
la interfaz.
