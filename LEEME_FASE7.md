# ARUS MARK 7 — FASE 7: Verifier

## Como instalar
Añade/sustituye estos archivos (mismas rutas):

    brain/verifier.py              (nuevo)
    brain/brain.py                 (modificado)
    ai/providers/local_provider.py (modificado)

Requiere las Fases 2-6 ya instaladas (usa ConversationManager,
ContextManager, Planner, TaskManager, ToolManager, ToolAgent). No se
toco `arus/interface/*` en esta fase.

## Auditoria previa
Se busco cualquier verificador existente ("verif" en todo el
proyecto) antes de escribir nada: no habia ninguno. Fase 7 es
infraestructura nueva, no la ampliacion de algo que ya existiera —
al contrario que las fases anteriores, donde casi siempre habia
codigo muerto que revivir.

## Que se implemento
`brain/verifier.py` — clase `Verifier`, con alcance deliberadamente
acotado a resultados ESTRUCTURADOS (tareas de herramientas,
respuestas de agentes), tal como pide el punto 15 del prompt maestro
("codigo, resultados, archivos, herramientas, calculos, tareas,
modificaciones"):

    verify_task(task)              -> VerificationResult
    verify_plan(tasks)              -> (ok, [VerificationResult...])
    verify_agent_response(response) -> VerificationResult
    repair_task(task, executor)     -> reintenta UNA vez, verifica de nuevo
    repair_agent(request, retry)    -> reintenta UNA vez, verifica de nuevo

No se implemento verificacion de respuestas de texto libre del chat
normal — verificar que una respuesta conversacional es "correcta"
necesitaria que el propio modelo se autoevalue, y fingir esa
verificacion con reglas simples habria sido peor que no tenerla.
Queda fuera de esta fase, dicho explicitamente en el docstring del
modulo.

## Donde se engancho (ciclo PLAN -> EXECUTE -> VERIFY -> REPAIR/RETRY)

### ai/providers/local_provider.py (ciclo de herramientas de la Fase 6)
Antes: tras ejecutar el plan de tareas, el resultado -incluidos los
fallos- se pasaba al modelo sin comprobarlo.
Ahora: se verifica cada tarea; las que fallan (`status == "error"`)
se reintentan UNA vez contra `ToolManager.execute`; se pase o no ese
reintento, el resultado final (reparado o el fallo honesto) es lo que
llega al modelo.

### brain/brain.py (rama `intent == "tool"`, ToolAgent)
Antes: lo que devolviera `ToolAgent.execute()` (exito o fallo) se
aceptaba tal cual.
Ahora: se verifica la `AgentResponse`; si `success` es `False`, se
reintenta UNA vez `agent.execute(request)` antes de devolver el
resultado final.

## Probado (con stubs de PySide6/ollama, no instalados en mi entorno)
1. `verify_task`: caso correcto, caso con error, caso con resultado
   vacio — los tres bien clasificados.
2. `repair_task`: reintento que esta vez funciona (repara), y
   reintento que tambien falla (se reporta honestamente, sin
   inventar un resultado).
3. `verify_agent_response`: exito y fallo (con motivo extraido de
   `errors`) bien clasificados.
4. Integracion real: el modelo pide una herramienta que no existe ->
   la tarea queda en `status="error"` -> Verifier lo detecta -> se
   reintenta -> sigue sin existir -> el modelo recibe
   "Fallo tras reintento: Herramienta 'x' no encontrada." en vez de
   que el flujo se rompa o se le mienta con un resultado inventado.
5. Caso de division por cero: `CalculatorTool` ya capturaba ese error
   internamente y devolvia un string explicativo (no lanzaba
   excepcion) -> Verifier lo trata como tarea completada con
   resultado (que es correcto: la herramienta funciono, solo que el
   calculo no era valido) -> no dispara reparacion innecesaria.
6. Regresion completa de Fases 2-6: `Brain.think()` normal, memoria
   de nombre, persistencia de conversacion, rama `intent==tool` — sin
   cambios de comportamiento salvo el propio Verifier.
7. Interfaz: `main_window.py`, `controller.py`, `core_visual.py`
   identicos byte a byte al original.
8. Sintaxis de todo el proyecto (`py_compile`): OK.

## FASE 7 — RESULTADO

Archivos creados:
- brain/verifier.py

Archivos modificados:
- brain/brain.py (import + instancia de Verifier; VERIFY/REPAIR en la
  rama de ToolAgent)
- ai/providers/local_provider.py (VERIFY/REPAIR en el ciclo de
  tool-calling de la Fase 6)

Archivos NO modificados:
- arus/interface/* (identico byte a byte)
- conversations/*, context/*, memory/*, agents/* (sin tocar)

Pruebas:
- Verifier (unitarias): OK
- Repair/retry (exito tras reintento y fallo honesto tras reintento): OK
- Integracion con el ciclo de herramientas real: OK
- Sin regresion en Fases 2-6: OK
- Interfaz visual: sin cambios
- Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
  entorno (paquetes no instalados aqui) — confirmalo en tu maquina.

Pendiente para siguientes fases: Fase 8 (RAG + documentos +
proyectos), Fase 9 (Git/GitHub), Fase 10 (asistente de programacion),
y de ahi en adelante voz, vision, tareas autonomas, seguridad,
plugins y evaluacion (Fases 11-16). Sigue pendiente tambien la
decision sobre la arquitectura de agentes duplicada que se audito en
la Fase 6 (CoordinatorAgent/CoderAgent/ResearchAgent/FileAgent sin
`execute()` real).
