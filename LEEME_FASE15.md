# ARUS MARK 7 — FASE 15: Plugins

## Como instalar
Añade/sustituye (mismas rutas):

    plugins/plugin.py            (modificado)
    plugins/plugin_manager.py    (modificado)
    plugins/installed/__init__.py (nuevo, carpeta vacia por defecto)
    tools/tool_manager.py        (modificado)

No se toco `arus/interface/*`, `plugins/plugin_registry.py` ni
`plugins/examples/test_plugin.py`.

## Auditoria previa
Ya existia una base solida: `Plugin` (ABC), `PluginManager`,
`PluginRegistry`, y un plugin de ejemplo. Pero `load()` exigia que
alguien construyera el objeto Plugin a mano; no habia descubrimiento
automatico (a diferencia de `ToolManager`, que si escanea `tools/`
solo). Y nada en el proyecto instanciaba `PluginManager` -- estaba
tan muerto como Planner/TaskManager antes de la Fase 6. No se
reescribio desde cero: se amplio lo que ya habia.

## Que se añadio
1. **Descubrimiento automatico real**, mismo patron que ya usa
   `ToolManager` para `tools/`: `PluginManager.discover(directory)` y
   `load_all(directory, tool_manager=None)` escanean
   `plugins/installed/` (vacia por defecto -- nada se activa sin que
   tu pongas algo ahi a proposito).
2. **Los plugins pueden aportar herramientas de verdad** (punto 42):
   `Plugin.get_tools()` es un hook opcional (por defecto `[]`, no
   rompe `TestPlugin` ni ningun plugin existente que no lo
   implemente). Si lo implementas, esas herramientas se registran en
   el `ToolManager` real -- probado de extremo a extremo: un plugin
   de prueba aporto una tool, y el modelo pudo ejecutarla via
   `ToolManager.execute()` como cualquier otra.
3. **`ToolManager.register(tool)`** (metodo nuevo, aditivo): permite
   añadir una herramienta ya instanciada sin volver a escanear
   `tools/`. No cambia `load_tools()`.
4. **Fallos contenidos** (punto 45): si un plugin falla al importarse
   (modulo que no existe) o al inicializarse (excepcion en
   `initialize()`), NO tumba a ARUS ni a los demas plugins. Se
   registra el motivo en `failed`, no se silencia ni se finge exito.
5. **Auditoria real** (punto 41): cada carga, descubrimiento fallido
   o descarga de plugin queda en `logs/audit.log`.

## Seguridad: lo que SI se garantiza y lo que NO (honesto)
El punto 42 pide "los plugins no deben tener acceso ilimitado al
sistema". Esto NO implementa un sandbox de ejecucion real (procesos
separados, limites de CPU/memoria) -- eso es un proyecto en si mismo
y no se finge aqui, siguiendo el mismo criterio que con
`git commit` (Fase 9) y el sandbox falso que se encontro en
`file_tool.py` (Fase 14): mejor no tener una proteccion que fingir
una que no protege nada.

Lo que si se garantiza, de verdad:
- Solo se cargan plugins desde una carpeta explicita
  (`plugins/installed/`), no desde cualquier ruta que alguien
  indique en caliente.
- Un plugin roto no puede tumbar el resto del sistema.
- Las herramientas de un plugin se ejecutan a traves del mismo
  `ToolManager` de siempre -- si en el futuro se añaden mas limites
  de permisos por herramienta (ver Fase 14, PathGuard/ShellGuard),
  se aplicarian igual a las de un plugin, porque pasan por el mismo
  sitio.

## Probado
1. Retrocompatibilidad: el `TestPlugin` original sigue cargando igual
   con `load()` manual (get_tools() por defecto = []).
2. Descubrimiento automatico real: un plugin de prueba (creado para
   la ocasion, en una carpeta temporal) que aporta una herramienta
   "saludo" -- se descubrio solo, se cargo, la herramienta aparecio
   en `ToolManager.available_tools()`, y se ejecuto de verdad
   devolviendo el resultado esperado.
3. **Caso critico de robustez:** tres plugins a la vez -- uno bueno,
   uno que falla al importar (modulo inexistente), uno que falla en
   `initialize()`. El bueno se cargo con normalidad; los otros dos
   quedaron en `failed` con el motivo exacto, sin tumbar nada.
4. `logs/audit.log` registro las 4 operaciones (carga OK, fallo de
   import, carga OK del bueno, fallo de init) con su motivo.
5. Regresion completa: `ToolManager` sigue cargando todas las
   herramientas de fases anteriores (calculator, git, run_tests...);
   `Brain.think()` y la memoria de nombre siguen funcionando.
6. Interfaz identica byte a byte. Sintaxis de todo el proyecto: OK.

## FASE 15 — RESULTADO

Archivos creados:
- plugins/installed/__init__.py (carpeta nueva, vacia por defecto)

Archivos modificados:
- plugins/plugin.py (hook get_tools() opcional, retrocompatible)
- plugins/plugin_manager.py (descubrimiento automatico, fallos
  contenidos, auditoria; load()/unload() manuales conservados)
- tools/tool_manager.py (metodo register() nuevo, aditivo)

Archivos NO modificados:
- arus/interface/*, plugins/plugin_registry.py,
  plugins/examples/test_plugin.py

Pruebas: 6 casos reales, incluyendo el caso de robustez con plugins
rotos a proposito. Interfaz visual: sin cambios. Arranque completo
con PySide6/Ollama reales: NO VERIFICADO en este entorno —
confirmalo en tu maquina.

Pendiente: hooks equivalentes para agentes/proveedores/comandos
(get_agents(), get_commands()...) si en algun momento tienes un
plugin real que los necesite -- no se crearon ganchos especulativos
sin nadie que los use; Fase 16 (Evaluacion), la ultima; decisiones
pendientes de fases anteriores (agentes duplicados, RAG, confirmacion
Git, STT duplicado, voz->Brain->voz, entrada de imagen, tareas largas
automaticas, PathGuard en GitTool).
