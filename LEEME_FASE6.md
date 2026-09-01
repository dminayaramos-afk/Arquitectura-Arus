# ARUS MARK 7 — FASE 6: Planner + Tools + Agents en un ciclo único

## Como instalar
Sustituye/añade estos archivos (mismas rutas):

    tools/calculator_tool.py       (estaba vacio, 0 bytes -> implementado)
    ai/providers/local_provider.py (modificado)

Nada mas. No se toco `arus/interface/*`, `brain/brain.py` ni
`agents/*` en esta fase.

## El hallazgo real (lo mas importante de esta fase)
`ai/providers/local_provider.py` YA le ofrecia al modelo las 15
herramientas reales de `tools/` via function-calling de Ollama
(`tools=self.tools.schemas()`, desde antes de esta fase). Pero si el
modelo pedia usar una, la respuesta se ignoraba por completo:

    return response.message.content   # con tool_calls, esto suele venir vacio

Es decir: ARUS le enseñaba las herramientas al modelo, el modelo
podia "pedirlas", y ARUS nunca las ejecutaba ni le devolvia el
resultado. Roto en silencio, sin error visible.

Tambien encontre que `tools/calculator_tool.py` estaba completamente
vacio (0 bytes) — `ToolManager` lo importaba sin fallar, pero no
registraba ninguna clase `BaseTool`, asi que "calculator" nunca
aparecia en la lista de herramientas ofrecidas al modelo, contradiciendo
el ejemplo explicito del punto 16 ("Calculo -> Calculator").

## Que se corrigio
### 1. tools/calculator_tool.py
Implementado con evaluacion segura por AST (mismo enfoque ya probado
en `agents/tool_agent.py`, sin usar `eval()`).

### 2. ai/providers/local_provider.py — el ciclo real
Ahora, si el modelo pide herramientas:

1. Se construye un `Task` por cada llamada (via `Planner.create_plan`,
   que existia pero nunca se llamaba desde ningun sitio).
2. `TaskManager.execute_plan(self.tools)` las ejecuta de verdad sobre
   `ToolManager` (tambien existia sin usarse desde aqui).
3. El resultado real se añade a los mensajes como turno `role: tool`
   y se vuelve a llamar a Ollama para que de la respuesta final en
   lenguaje natural, con el dato real ya en la mano.
4. Limite de 4 rondas para evitar un bucle infinito si el modelo
   insistiera en pedir herramientas sin parar.

Esto revive tres clases que ya existian en el proyecto pero estaban
completamente muertas (`brain.planner.Planner`,
`brain.task.Task`, `brain.task_manager.TaskManager`) usandolas para lo
que fueron diseñadas, en vez de crear una arquitectura nueva encima.

## Auditoria: arquitectura de agentes duplicada (NO tocada)
Al inspeccionar para esta fase encontre que el proyecto tiene DOS
sistemas de agentes incompatibles entre si:

**Sistema A (vivo, el que usa Brain):**
`agents.base_agent.BaseAgent` (interfaz `can_handle`/`execute`),
`agents.agent_registry.AgentRegistry`, `agents.agent_router.AgentRouter`,
`agents.tool_agent.ToolAgent` (el unico agente registrado hoy).

**Sistema B (huerfano, nada lo usa):**
`brain.agent.Agent` (dataclass con solo name/role/capabilities, SIN
`execute()`), `brain.agent_manager.AgentManager`,
`brain.agent_router.AgentRouter` (mismo nombre que el del Sistema A
pero incompatible), `brain.message.Message` +
`brain.message_bus.MessageBus`, `brain.router.Router`. Los cuatro
agentes especializados que pide el punto 17 del prompt maestro
(`agents/coordinator_agent.py`, `coder_agent.py`, `research_agent.py`,
`file_agent.py`) estan escritos contra este Sistema B: declaran
"capabilities" (python, git, debug / search, web, github_search /
file, file_writer, find_file...) pero NINGUNO implementa `execute()`
— son solo descriptores, no tienen logica real detras. Nada los
registra en ningun sitio.

No los conecte ni los borre porque:
- Fusionar ambos sistemas es una refactorizacion real de arquitectura,
  no un fix incremental — te corresponde decidir a ti cual conservar.
- Darles un `execute()` de verdad requeriria las capacidades de las
  Fases 9/10/24/25 (Git, ejecucion de codigo, archivos, busqueda web)
  que todavia no hemos hecho — inventarles una ejecucion falsa aqui
  seria justo el "fingir cambios" que me pediste evitar.

Mi recomendacion para cuando quieras abordarlo: lo mas simple es
migrar `CoderAgent`/`ResearchAgent`/`FileAgent` para que hereden de
`agents.base_agent.BaseAgent` en vez de `brain.agent.Agent`, y que su
`execute()` delegue en las herramientas de `tools/` que ya existen
(`file_tool.py`, `web_tool.py`, `github_search_tool.py`, etc. — casi
todas sus "capabilities" declaradas ya tienen una tool real
equivalente). Eso se podria hacer en una fase dedicada si quieres,
sin esperar a las Fases 9/10/24/25 completas.

## Probado
Con los mismos stubs de PySide6/ollama que las fases anteriores
(no instalados en mi entorno):

1. `calculator` aparece en `ToolManager.available_tools()`: OK.
2. Simule que Ollama pide `calculator(expression="6 * 7")`: se
   ejecuto de verdad y devolvio "42" (no se ignoro). OK.
3. Se hicieron las 2 llamadas a Ollama esperadas (pedir herramienta +
   responder con el resultado ya resuelto). OK.
4. El mensaje `role: tool` que vuelve al modelo contiene el resultado
   real ("42"), no un placeholder. OK.
5. Regresion completa de Fases 2-5: `Brain.think()` normal, memoria
   de nombre, persistencia de conversacion, y la rama `intent==tool`
   (ToolAgent, sin tocar) — todo sigue funcionando igual. OK.
6. Interfaz: `main_window.py`, `controller.py`, `core_visual.py`
   identicos byte a byte al original; `chat.py` solo con el cambio ya
   conocido de la Fase 4. OK.
7. Sintaxis de todo el proyecto (`py_compile`): OK.

## FASE 6 — RESULTADO

Archivos creados: (ninguno; calculator_tool.py existia vacio, se
rellenó)

Archivos modificados:
- tools/calculator_tool.py (estaba vacio, 0 bytes)
- ai/providers/local_provider.py (ciclo real de tool-calling)

Archivos NO modificados:
- brain/brain.py, brain/planner.py, brain/task.py,
  brain/task_manager.py (se usan tal cual estaban, sin cambiarles el
  codigo)
- agents/* (incluida la arquitectura duplicada encontrada — solo
  auditada, no tocada)
- arus/interface/* (identico byte a byte)

Pruebas:
- CalculatorTool registrada y funcional: OK
- Ciclo Planner -> TaskManager -> ToolManager ejecutando herramientas
  reales pedidas por el modelo: OK
- Resultado real devuelto al modelo (no ignorado): OK
- Sin regresion en Fases 2-5: OK
- Interfaz visual: sin cambios
- Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
  entorno (paquetes no instalados aqui) — confirmalo en tu maquina.

Pendiente para siguientes fases: Verifier (Fase 7 — plan/execute ya
existen, falta el paso de verificacion con reintento/reparacion);
decidir que hacer con la arquitectura de agentes duplicada (auditada
arriba); Fases 8-16 (RAG, Git, codigo, voz, vision, tareas autonomas,
seguridad, plugins, evaluacion).
