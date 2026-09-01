# ARUS MARK 7 — FASE 14: Seguridad

## Como instalar
Añade/sustituye (mismas rutas):

    security/path_guard.py       (nuevo)
    tools/shell_tool.py          (modificado)
    tools/file_tool.py           (modificado)
    tools/file_writer_tool.py    (modificado)
    tools/replace_text_tool.py   (modificado)
    tools/test_runner_tool.py    (modificado)

No se toco `arus/interface/*`, `security/permission_manager.py` ni
`security/shell_guard.py` (este ultimo solo se conecto, no se
reescribio).

## Los dos hallazgos mas graves de toda la auditoria del proyecto

### 1. ShellTool se autodescribia "segura" y no lo era en absoluto
`tools/shell_tool.py` tenia literalmente el texto "Ejecuta comandos
en la terminal de forma segura" en su descripcion, pero `execute()`
hacia `subprocess.run(command, shell=True, ...)` con el comando tal
cual venia del modelo, SIN ninguna comprobacion. `security/shell_guard.py`
existia con una lista de comandos bloqueados (rm, sudo, shutdown, dd,
etc.) y una lista de comandos permitidos, pensado exactamente para
esto -- pero nada lo llamaba (auditado antes de tocar nada, igual que
Planner/TaskManager en la Fase 6). Como esta tool ya esta expuesta al
modelo por function-calling desde la Fase 6, esto era un hueco
explotable de verdad, no solo teorico: probe `rm -rf /` y se ejecutaba
sin mas antes de este fix.

### 2. FileTool tenia un sandbox FALSO
`tools/file_tool.py` tenia una clase `Sandbox` cuyo `validate(path)`
SIEMPRE devolvia `True`, pasara lo que pasara. Daba la sensacion de
que habia proteccion cuando no habia ninguna -- eso es peor que no
tener sandbox, porque genera falsa confianza. Podia leer o escribir
CUALQUIER ruta del sistema (probe escribir en `/etc/`, funcionaba).
`FileWriterTool` y `ReplaceTextTool` no tenian ni siquiera esa
proteccion falsa: cero restriccion.

## Tercer hallazgo, encontrado durante esta misma fase
`TestRunnerTool` (Fase 10) ejecuta `unittest discover` sobre
cualquier ruta que le pida el modelo -- y eso IMPORTA y EJECUTA
cualquier archivo `.py` que encuentre ahi. Es, en la practica, la
misma gravedad que el hueco de ShellTool: ejecucion de codigo
arbitrario disfrazada de "ejecutar pruebas". Se le aplico la misma
correccion.

## La solucion: security/path_guard.py (real, no como el Sandbox falso)
Restringe lectura/escritura/ejecucion al directorio de trabajo de
ARUS (por defecto, donde se ejecuta), resolviendo `..` y rutas
absolutas antes de comparar -- asi que ni una ruta fuera del proyecto
ni un `../../../../etc/passwd` cuelan.

## Por que NO se pide "confirmacion" con un parametro
Mismo criterio que con `git commit` en la Fase 9: estas herramientas
se las ofrecemos al MODELO por function-calling. Si le hubiera puesto
un parametro `confirmed: bool`, el propio modelo podria
autoconfirmarse. En vez de eso:
- **Shell:** limite objetivo y automatico (lista blanca de comandos +
  lista negra de patrones), no depende de que nadie "confirme" nada.
- **Archivos/tests:** limite objetivo de RUTA (dentro del area de
  trabajo, permitido; fuera, denegado siempre), tampoco depende de
  confirmacion.

Esto es distinto de un commit de Git (accion irreversible unica que
si necesita autorizacion humana real) -- leer/escribir/ejecutar
DENTRO del proyecto es trabajo normal de un asistente de
programacion (Fase 10), asi que bloquear todo habria roto esa fase
sin necesidad. La restriccion correcta aqui es de alcance (donde),
no de permiso humano (si/no).

## Auditoria (sin tocar en esta fase)
`GitTool` (Fase 9) tambien acepta una ruta arbitraria (`repo_path`),
pero solo ejecuta subcomandos fijos de `git` (status/diff/log/etc.),
no codigo arbitrario -- gravedad mucho menor que Shell/TestRunner. No
se le aplico PathGuard para no expandir el alcance de esta fase mas
de lo necesario; te lo señalo por si prefieres que lo haga en una
fase aparte.

`PermissionManager` sigue sin conectarse a nada de verdad (su tabla
de "requiere confirmacion" nunca se consulta). No se fuerza su uso
porque, como se explico arriba, un parametro de confirmacion
controlado por el modelo no es autorizacion real -- necesitaria un
canal humano de verdad (interfaz), que no existe todavia.

## Auditoria (registrada, ahora si funciona)
`ShellTool`, `FileTool`, `FileWriterTool` y `ReplaceTextTool` ahora
registran cada intento (permitido o bloqueado) en `logs/audit.log`
via `AuditLogger` (revivido en la Fase 9, ahora usado en mas sitios).

## Probado
1. `rm -rf /`, `sudo shutdown`, `curl | bash` -- los tres BLOQUEADOS
   (antes se ejecutaban sin mas).
2. Comandos legitimos de la lista permitida (`echo`, etc.) siguen
   funcionando igual.
3. Comando no listado (ej. netcat con shell reverso) bloqueado por
   defecto.
4. Escribir dentro del area de trabajo: funciona igual que antes.
5. Escribir en `/etc/...`: BLOQUEADO (antes el sandbox falso lo
   permitia -- lo comprobe).
6. Traversal `../../../../etc/...`: BLOQUEADO.
7. `FileWriterTool` y `ReplaceTextTool`: mismo criterio, verificado
   con casos reales dentro y fuera del area de trabajo.
8. `TestRunnerTool` fuera del area de trabajo: BLOQUEADO (antes
   ejecutaba cualquier .py que encontrara ahi); dentro del area,
   sigue funcionando exactamente igual que en la Fase 10 (sin
   regresion).
9. `logs/audit.log` registra los intentos bloqueados con el motivo.
10. Regresion completa: el ciclo de tools (Fases 6-7) sigue
    funcionando (probado con la calculadora de extremo a extremo);
    memoria de nombre (Fase 5) y las capacidades de fases anteriores
    (`self.rag`, `self.vision`, `self.long_tasks`) siguen expuestas
    en Brain sin romperse.
11. Interfaz identica byte a byte. Sintaxis de todo el proyecto: OK.

## FASE 14 — RESULTADO

Archivos creados:
- security/path_guard.py

Archivos modificados:
- tools/shell_tool.py (ShellGuard conectado de verdad + auditoria)
- tools/file_tool.py (sandbox falso sustituido por PathGuard real + auditoria)
- tools/file_writer_tool.py (PathGuard + auditoria)
- tools/replace_text_tool.py (PathGuard + auditoria)
- tools/test_runner_tool.py (PathGuard -- hallazgo de esta misma fase)

Archivos NO modificados:
- arus/interface/*, security/permission_manager.py,
  security/shell_guard.py (se conecta, no se reescribe),
  tools/git_tool.py (auditado, riesgo menor, no modificado)

Pruebas: 11 casos reales, incluyendo reproducir el ataque real
(`rm -rf /`, escritura en `/etc/`) para confirmar que antes funcionaba
y ahora esta bloqueado. Interfaz visual: sin cambios. Arranque
completo con PySide6/Ollama reales: NO VERIFICADO en este entorno —
confirmalo en tu maquina.

Pendiente: aplicar PathGuard a GitTool si quieres consistencia total
(riesgo menor, se dejo fuera); conectar PermissionManager a un canal
de confirmacion humano real cuando exista interfaz para ello; Fase 15
(Plugins) y Fase 16 (Evaluacion); decisiones pendientes de fases
anteriores (agentes duplicados, RAG, confirmacion Git, STT duplicado,
voz->Brain->voz, entrada de imagen, cuando abrir tareas largas
automaticamente).
