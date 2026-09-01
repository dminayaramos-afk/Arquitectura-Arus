# ARUS MARK 7 — FASE 16: Evaluación automática (última fase)

## Como instalar
Añade/sustituye (mismas rutas):

    evaluation/__init__.py       (nuevo)
    evaluation/check.py          (nuevo)
    evaluation/suite.py          (nuevo)
    tools/web_tool.py            (modificado)
    tools/search_tool.py         (modificado)

No se toco `arus/interface/*`.

## Como ejecutarla
Desde la raiz del proyecto:

    python -c "from evaluation.suite import run_all; print(run_all().report())"

O crea un `evaluar.py` de una linea con ese mismo contenido si
prefieres `python evaluar.py`. Se recomienda ejecutarla antes y
despues de cualquier cambio importante (punto 50 del prompt maestro).

## Dos hallazgos de "fingir cambios" que encontre ANTES de poder evaluar nada
Al preparar la categoria "Web" de la evaluacion me di cuenta de que no
tenia sentido "evaluar" una capacidad que era pura ficcion:

- `tools/web_tool.py`: `execute()` devolvia SIEMPRE
  `"Contenido simulado para la URL: {url}"`, sin hacer ninguna
  peticion real, para cualquier URL.
- `tools/search_tool.py`: `execute()` devolvia SIEMPRE
  `"Resultados para la búsqueda: {query}"`, sin buscar nada de
  verdad.

Las corregi antes de escribir la evaluacion:
- `WebTool` ahora hace un GET real (pensado para APIs/contenido
  crudo; para extraer texto legible de una pagina, sigue existiendo
  `web_reader`, que ya era real desde antes).
- `SearchTool` ahora busca de verdad en el endpoint HTML de
  DuckDuckGo (no necesita clave de API ni registro).

En el entorno donde desarrolle esto la red esta restringida (solo
puedo llegar a hosts en una lista blanca), asi que no pude confirmar
una respuesta real completa -- pero confirme que las peticiones SI
son reales: la URL de ejemplo devolvio un HTTP 403 real del proxy de
red (no el texto simulado de antes), y la busqueda devolvio un error
de conexion real. La evaluacion marca esto como "no verificable en
este entorno" en vez de darlo por bueno o por malo sin pruebas -- en
tu maquina, con red normal, deberian funcionar y la evaluacion lo
confirmaria en verde.

## Que cubre la bateria (punto 50 del prompt maestro)
Contexto, Memoria, Conversación larga, Herramientas, Código, Web,
RAG, Archivos, Voz, Errores, Seguridad, Tareas, Agentes -- las 13
categorias que pide el punto 50, mas una categoria "Integración" con
Brain de extremo a extremo. 32 pruebas en total.

Varias pruebas son deliberadamente REGRESIONES DIRECTAS de bugs
graves encontrados en fases anteriores, para que si alguien los
reintroduce sin querer, la evaluacion lo detecte:
- "VoiceCore() no falla sin vosk" -- el bug mas grave del proyecto
  (Fase 11): que tumbaba TODA la interfaz si vosk no estaba
  instalado.
- "ShellTool bloquea comandos peligrosos" y "PathGuard bloquea path
  traversal" -- los dos huecos de seguridad reales de la Fase 14.
- "escritura fuera del área de trabajo bloqueada".
- "no se puede avanzar una tarea pausada" -- el bug de la Fase 13.
- "un plugin roto no tumba a los demás" -- el comportamiento clave
  de la Fase 15.

## Resultado de ejecutarla contra el proyecto real ahora mismo
27 de 27 pruebas verificables: OK. 0 fallos. 4 no verificables en
este entorno de forma honesta (web/busqueda por red restringida,
fallo de conexion a Ollama por disponibilidad de mocks, y vision por
no tener Ollama accesible aqui) -- ninguna se dio por buena sin
comprobarla.

## FASE 16 — RESULTADO

Archivos creados:
- evaluation/__init__.py, evaluation/check.py, evaluation/suite.py

Archivos modificados:
- tools/web_tool.py (peticion HTTP real, ya no simulada)
- tools/search_tool.py (busqueda real via DuckDuckGo, ya no simulada)

Archivos NO modificados:
- arus/interface/*, tools/web_reader_tool.py (ya era real)

Pruebas: 32 casos en 13 categorias + integracion. 27 OK, 0 fallos, 4
SKIP honestos. Interfaz identica byte a byte. Sintaxis de todo el
proyecto: OK.

---

## CIERRE DEL PROYECTO ARUS MARK 7 -- LAS 16 FASES

Con esta entrega se completan las 16 fases del prompt maestro. Cada
una se entrego por separado con su propio tar.gz, LEEME y pruebas
reales; este es el resumen final.

Hecho y probado de verdad, sin fingir:
 1. Auditoria/limpieza (sesion previa)
 2. ConversationManager
 3. ContextManager
 4. Cerebro unificado (Chat -> Controller -> Brain -> ModelManager)
 5. Memoria multinivel
 6. Planner + Tools + Agents en un ciclo real
 7. Verifier (VERIFY -> REPAIR/RETRY)
 8. RAG (embeddings ligeros, decision por hardware limitado)
 9. Git (solo lectura; commit rechaza honestamente)
10. Asistente de programacion (test_runner_tool)
11. Voz (con el hallazgo mas grave de todo el proyecto, corregido)
12. Vision (honesta sobre disponibilidad de modelo)
13. Tareas autonomas (persistentes, sobreviven a reinicio)
14. Seguridad (dos huecos reales cerrados: shell y sandbox de archivos)
15. Plugins (descubrimiento automatico, fallos contenidos)
16. Evaluacion automatica (esta entrega)

La interfaz original de ARUS no se toco en ninguna fase -- verificado
byte a byte cada vez.

## Decisiones de producto que quedan pendientes de que decidas tu
Estas NO son bugs ni trabajo a medias -- son puntos donde segui
construyendo sobre lo que habia sin forzar una decision que te
corresponde a ti:

1. **Arquitectura de agentes duplicada** (Fase 6): hay dos sistemas de
   agentes incompatibles en el proyecto; uno vivo, uno huerfano del
   que dependen Coordinator/Coder/Research/FileAgent sin execute()
   real.
2. **Cuando conectar RAG a Brain automaticamente** (Fase 8): la
   capacidad existe y funciona, pero decidir cuando se dispara en una
   conversacion normal es una decision de producto.
3. **Confirmacion humana real para git commit/push** (Fase 9): no
   implementado a proposito, porque el modelo no puede autorizarse a
   si mismo; necesitaria un canal de confirmacion en la interfaz.
4. **Tres implementaciones de STT duplicadas** (Fase 11): solo una
   esta conectada; las otras dos son codigo muerto sin fusionar.
5. **Conectar voz -> Brain -> voz de punta a punta** (Fase 11):
   necesitaria una linea nueva en `main_window.py` (pasarle el
   controller a VoiceCore) que no se toco sin tu autorizacion.
6. **Via real para pasarle una imagen a ARUS desde la interfaz**
   (Fase 12): hoy no existe ningun control de subida/pegado de
   imagenes en la GUI.
7. **Cuando Brain abre una tarea larga automaticamente** (Fase 13):
   la infraestructura esta lista, falta decidir el disparador.
8. **PathGuard en GitTool** (Fase 14): se dejo fuera por ser de menor
   riesgo; se podria añadir por consistencia.
9. **Hooks de plugin para agentes/proveedores/comandos** (Fase 15):
   solo se implemento el de herramientas, que es el que tenia un caso
   de uso real y probado.

Mi recomendacion: instala las 16 entregas en orden en tu maquina real
(con PySide6, Ollama, y opcionalmente vosk/espeak-ng/pytest
instalados), confirma que ARUS arranca y se comporta igual que antes
visualmente, y luego dime cual de estas 9 decisiones quieres abordar
primero -- o si prefieres que profundice en alguna fase concreta con
mas capacidad de la que le di en esta primera pasada.
