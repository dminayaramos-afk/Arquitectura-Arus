# ARUS MARK 7 — FASE 4: Unificar Chat -> Controller -> Brain -> ModelManager

## Lo que encontre al inspeccionar
`main_window.py` YA hacia `ChatWidget(self.controller)` — el controller
se pasaba correctamente. El problema estaba solo dentro de
`ChatWidget.send()`: ignoraba ese `self.controller` y hacia su propio
`requests.post` directo a `http://127.0.0.1:11434/api/generate`,
exactamente el bug descrito en el punto 11 del prompt maestro.

`ARUSController.process()` (en `controller.py`) ya estaba bien
implementado: comandos -> `brain.think()` -> `ModelManager`. No hizo
falta tocar `controller.py` en absoluto.

## Riesgo real que encontre y corregi
El prompt de identidad de ARUS (nombre, creador Danny Jesus Minaya
Ramos, nunca decir Qwen/Alibaba) SOLO vivia dentro de esa llamada
directa que borre de `chat.py`. `ai/providers/local_provider.py` (el
unico sitio por donde ahora pasan TODAS las peticiones al modelo) no
lo tenia. Si solo hubiera cortado la ruta directa sin arreglar esto,
ARUS habria perdido su identidad la primera vez que alguien le
preguntara "quien te creo". Lo traslade a `local_provider.py`, que es
donde debe vivir de forma permanente (aplica sin importar quien llame
al modelo: chat, comandos, agentes futuros...).

## Como instalar
Sustituye estos dos archivos en tu proyecto (mismas rutas):

    arus/interface/chat.py
    ai/providers/local_provider.py

No hace falta tocar nada mas.

## Que cambio exactamente
### arus/interface/chat.py
Se elimino el bloque `import requests` + `requests.post(...)` a Ollama
dentro de `send()`. En su lugar:

    if self.controller is not None:
        response = self.controller.process(text)
    else:
        response = "ARUS no está conectado a su cerebro (controller no disponible)."

Nada mas cambio: mismo layout, mismos estilos, mismo QTextEdit/QLineEdit/
QPushButton, mismo formato "Usuario: "/"ARUS: ".

### ai/providers/local_provider.py
Se añadio la constante `ARUS_SYSTEM_PROMPT` (el mismo texto que antes
estaba hardcodeado en chat.py) y se inyecta como primer mensaje
`{"role": "system", ...}` en `generate()`, solo si el historial que
llega no trae ya un mensaje de sistema (para no duplicarlo cuando
Fase 5/Brain empiece a construir historiales mas completos).

## Probado
No tengo PySide6 ni ollama instalados en este entorno de desarrollo
(sin conexion a internet aqui), asi que use stubs minimos SOLO para
poder ejecutar tu codigo real y comprobar la logica — los stubs no
forman parte de la entrega, no se instalan en tu proyecto.

Con esos stubs, ejecute la cadena completa de verdad:

1. `ARUSController().process("Hola ARUS")` -> recorre comandos,
   despues `Brain.think()` -> `ModelManager.generate()` ->
   `LocalProvider.generate()` -> devuelve respuesta. OK.
2. El primer mensaje que llega a `ollama.Client.chat()` es
   `{"role": "system", ...}` y contiene "Danny Jesus" y "Qwen" (la
   identidad se conserva). OK.
3. `ChatWidget.send()` real: escribi texto en el input, llame a
   `send()`, y verifique que el historial del chat contiene
   "Usuario: ..." y "ARUS: ..." — y que la respuesta vino de
   `controller.process()`, no de una llamada de red directa. OK.
4. Confirme por texto que `chat.py` ya no contiene ni "requests" ni
   "11434". OK.
5. Verifique que `main_window.py`, `controller.py` y
   `core_visual.py` son byte a byte identicos al original — cero
   cambios de interfaz visual. OK.

## Lo que NO se hizo (pendiente, no es esta fase)
- `brain.think()` sigue usando `WorkingMemory` (memoria simple en
  RAM) para el historial que le pasa a `ModelManager.generate()` —
  todavia NO usa `ConversationManager`/`ContextManager` (Fase 2/3).
  Conectar eso es Fase 5 (mejorar MemoryManager) o una fase de
  integracion de memoria: haria falta decidir, por ejemplo, que
  `conversation_id` usar dentro de `Brain` (hoy `Brain` no sabe en
  que conversacion esta), y eso implica tocar `brain.py`, que no
  estaba autorizado a modificar sin verlo primero contigo.
- No se probo contra Ollama real ni PySide6 real (no disponibles en
  este entorno) — te recomiendo confirmarlo en tu maquina.
- `ToolAgent`/`intent_detector` no se tocaron.

## FASE 4 — RESULTADO

Archivos creados: (ninguno)

Archivos modificados:
- arus/interface/chat.py (unico cambio funcional en interfaz: send()
  ya no llama a Ollama directamente)
- ai/providers/local_provider.py (restaura el system prompt de
  identidad de ARUS en el punto unico por el que ahora pasan todas
  las peticiones)

Archivos NO modificados:
- arus/interface/main_window.py (verificado identico byte a byte)
- arus/interface/controller.py (verificado identico byte a byte;
  ya estaba bien implementado)
- arus/interface/core_visual.py (verificado identico byte a byte)
- brain/brain.py
- ai/model_manager.py
- conversations/*, context/* (Fase 2 y 3, sin tocar)

Pruebas:
- Sintaxis (py_compile / AST): OK
- Cadena Controller -> Brain -> ModelManager -> LocalProvider: OK
- Identidad ARUS preservada en el system prompt: OK
- ChatWidget.send() usa el controller, no Ollama directo: OK
- Interfaz visual sin cambios (diff byte a byte): OK
- Arranque completo de ARUS con PySide6/Ollama reales: NO VERIFICADO
  en este entorno (paquetes no instalados aqui, sin red) — probado
  con stubs que ejercitan tu codigo real; confirmalo tu en tu maquina.

Pendiente para siguientes fases: conectar `Brain` con
`ConversationManager`/`ContextManager` (Fase 5, memoria), Planner +
Tools + Agents en un ciclo unico (Fase 6), Verifier (Fase 7), y el
resto de fases 8-16.
