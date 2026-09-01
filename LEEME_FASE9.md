# ARUS MARK 7 — FASE 9: Git/GitHub

## Como instalar
Añade este archivo (ruta nueva, no sustituye nada):

    tools/git_tool.py

`ToolManager` lo detecta automaticamente (escanea `tools/` al
arrancar, igual que hizo con `calculator_tool.py` en la Fase 6) — no
hace falta registrarlo en ningun otro sitio. No se toco
`arus/interface/*`, `brain/brain.py` ni ningun otro archivo.

## Auditoria previa
Ya existian `tools/github_clone_tool.py` (clona por URL) y
`tools/github_search_tool.py` (busca repos publicos por API). Lo que
faltaba, y es el nucleo del punto 21, es examinar un repositorio Git
LOCAL: status, diff, commits, ramas. Eso es lo que añade esta fase,
sin tocar los dos que ya funcionaban.

## Decision de seguridad importante (por que "commit" no hace nada)
El punto 21 pide "crear commits bajo autorizacion" y el punto 40
"Push remoto -> confirmar". El problema real: estas herramientas se
las ofrecemos al MODELO por function-calling (Ollama). Quien "pide"
ejecutar la accion es el modelo, no un humano pulsando un boton. Si le
hubiera puesto un parametro `confirmed: bool` a la herramienta, nada
impide que el propio modelo se auto-confirme sus comits — eso no es
autorizacion real, es fingirla. Como la interfaz (intocable) todavia
no tiene un mecanismo para pedirle confirmacion a un humano de verdad
y esperarla, implementar un commit "que funcione" aqui habria creado
justo el agujero de seguridad que me pediste evitar.

Por eso `action="commit"` existe en la herramienta pero SIEMPRE
devuelve una explicacion honesta de por que no se ejecuta, en vez de
fingir que funciona. No se implemento `push` en absoluto (ni con
excusa de "requiere confirmacion" ni de ninguna otra forma) — no
tiene sentido construir la parte peligrosa de esto antes que el
mecanismo de autorizacion real.

## Que SI hace GitTool (solo lectura, probado contra un repo real)
    status          -> git status --short --branch
    diff             -> git diff (cambios sin commitear)
    log               -> git log --oneline (ultimos N commits)
    branches          -> git branch --all
    current_branch    -> git rev-parse --abbrev-ref HEAD
    readme            -> lee README.md/.rst/.txt del repositorio

Valida antes de ejecutar nada: que la ruta existe, y que es
realmente un repositorio Git (`git rev-parse --is-inside-work-tree`).

## AuditLogger, revivido de verdad
`security/audit_logger.py` existia en el proyecto pero nada lo
llamaba (auditado antes de escribir, igual que con Planner/TaskManager
en la Fase 6). `GitTool` ahora SI lo usa: cada consulta (accion,
argumentos, resultado) queda en `logs/audit.log`, tal como pide el
punto 41. `security/permission_manager.py` sigue sin conectarse a
nada -- no lo fingi, porque `GitTool` ya rechaza `commit` por su
cuenta de forma honesta; conectar `PermissionManager` a una
aplicacion real de permisos (mas alla de Git) queda para la Fase 14
(Seguridad).

## Probado
Cree un repositorio Git real de prueba (`git init`, un commit, un
cambio sin commitear, una rama nueva) y ejecute las 6 acciones de
lectura contra el -- devolvieron exactamente lo esperado (rama
actual, diff real, log real, etc.). Probe tambien: `commit` (rechazo
honesto), una ruta que existe pero no es repo Git (error claro), y
una ruta que no existe (error claro). Confirme que `logs/audit.log`
registro cada llamada. Confirme que `ToolManager` detecta `git`
automaticamente y lo ejecuta bien via `.execute()`. Regresion
completa: `Brain.think()` normal y memoria de nombre (Fases 2-8)
siguen funcionando igual. Interfaz identica byte a byte. Sintaxis de
todo el proyecto: OK.

## FASE 9 — RESULTADO

Archivos creados:
- tools/git_tool.py

Archivos modificados: (ninguno)

Archivos NO modificados:
- arus/interface/*, brain/brain.py, security/permission_manager.py,
  tools/github_clone_tool.py, tools/github_search_tool.py

Pruebas:
- Las 6 acciones de lectura contra un repo Git real: OK
- Rechazo honesto de "commit": OK
- Manejo de rutas invalidas/no-git: OK
- AuditLogger registrando de verdad: OK
- ToolManager detecta y ejecuta la herramienta: OK
- Sin regresion en Fases 2-8: OK
- Interfaz visual: sin cambios
- Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
  entorno (paquetes no instalados aqui) — confirmalo en tu maquina.

Pendiente: comits/push reales (necesitan un mecanismo de confirmacion
humana en la interfaz que hoy no existe); "identificar codigo
duplicado"/"detectar problemas de arquitectura" del punto 21 (necesitan
razonamiento del modelo sobre el RAG de la Fase 8, no una herramienta
aislada -- se podria combinar en una fase posterior); ayuda con pull
requests (necesitaria token de GitHub y API de escritura, no
implementado). Fase 10 (asistente de programacion) en adelante hasta
Fase 16. Sigue pendiente tambien la decision sobre la arquitectura de
agentes duplicada (Fase 6).
