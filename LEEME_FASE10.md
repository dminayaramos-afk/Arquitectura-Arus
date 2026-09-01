# ARUS MARK 7 — FASE 10: Asistente de programación

## Como instalar
Añade este archivo (ruta nueva):

    tools/test_runner_tool.py

`ToolManager` lo detecta automaticamente. No se toco ningun otro
archivo.

## Auditoria previa: casi todo el punto 18 ya estaba cubierto
Antes de escribir nada revise que ya cubre cada capacidad que pide el
punto 18:

    leer codigo          -> tools/file_tool.py (ya existia)
    localizar archivos    -> tools/find_file_tool.py (ya existia)
    detectar errores (sintaxis) -> tools/python_check_tool.py (ya existia)
    generar/modificar/refactorizar codigo -> el modelo mismo +
                             tools/file_writer_tool.py, replace_text_tool.py
                             (ya existian) -- no hace falta una
                             "herramienta" nueva para esto, es lo que
                             el modelo ya hace al responder en texto
    crear documentacion/tests -> igual, el modelo + file_writer_tool
    revisar cambios        -> tools/git_tool.py `diff` (Fase 9)

Lo unico que faltaba de verdad: EJECUTAR pruebas automatizadas y
ANALIZAR el resultado. Eso es lo unico que añade esta fase, para no
duplicar nada de lo que ya funcionaba.

## Decision: pytest si esta, si no unittest (sin instalar nada nuevo)
Comprobe si pytest estaba instalado en el proyecto -- no lo esta
(punto 103: "¿es realmente necesaria? comprobar primero"). En vez de
forzar una dependencia nueva, `TestRunnerTool` detecta en tiempo de
ejecucion si pytest esta disponible y lo usa; si no, cae a `unittest`
(viene con Python, cero dependencias nuevas). Hoy en tu proyecto usara
`unittest`; si en algun momento instalas pytest, lo aprovechara solo.

## Bug real que encontre y arregle mientras probaba
Mi primer intento hacia `python -m unittest <ruta_de_archivo>` para
un archivo suelto -- eso esta mal, `unittest` interpreta ese
argumento como un nombre de modulo Python (con puntos), no como una
ruta de archivo, y falla con `ModuleNotFoundError` incluso con tests
que SI pasan. Lo detecte al probarlo de verdad (no me quede con la
primera version) y lo arregle usando siempre `unittest discover`,
ajustando la carpeta de inicio y el patron segun si la ruta es un
archivo o una carpeta.

## Decision sobre que cuenta como "fallo de la herramienta"
Que la suite de tests tenga fallos NO se trata como que la herramienta
fallo (no dispara el REPAIR/RETRY del Verifier de la Fase 7) --
ejecutar la suite y que de resultados en rojo es la herramienta
haciendo bien su trabajo, no un error tecnico. El texto que devuelve
deja clarisimo cuantas pruebas pasaron y cuantas no
("OK: todas las pruebas pasaron" / "FALLOS: hay pruebas que no
pasaron"), para que el modelo lo interprete y pueda proponer una
correccion.

## Probado
1. Cree un mini-proyecto con un test que pasa y otro que falla a
   proposito (`assertEqual(5-2, 100)`).
2. Ejecutar sobre la carpeta completa: detecto correctamente 1 fallo
   y 1 exito, con el traceback real incluido.
3. Ejecutar sobre solo el archivo que pasa: detecto correctamente
   "OK: todas las pruebas pasaron" (aqui encontre y arregle el bug de
   arriba).
4. Ruta inexistente: error claro.
5. Integracion real con el ciclo completo de las Fases 6+7: simule
   que el modelo pedia `run_tests`, se ejecuto de verdad, el
   resultado (con el fallo real) volvio al modelo, y `ToolManager` lo
   detecto automaticamente sin tocar nada mas.
6. Sin regresion: memoria de nombre (Fase 5) y el resto siguen
   funcionando igual.
7. Interfaz: identica byte a byte.
8. Sintaxis de todo el proyecto: OK.

## FASE 10 — RESULTADO

Archivos creados:
- tools/test_runner_tool.py

Archivos modificados: (ninguno)

Archivos NO modificados:
- arus/interface/*, brain/brain.py, tools/python_check_tool.py,
  tools/file_tool.py, tools/file_writer_tool.py,
  tools/replace_text_tool.py, tools/git_tool.py

Pruebas:
- Deteccion de fallos y exitos reales: OK
- Bug de rutas de archivo encontrado y corregido: OK
- Integracion con el ciclo Plan->Execute->Verify (Fases 6-7): OK
- Sin regresion en Fases 2-9: OK
- Interfaz visual: sin cambios
- Arranque completo con PySide6/Ollama reales: NO VERIFICADO en este
  entorno (paquetes no instalados aqui) — confirmalo en tu maquina.

Pendiente: analisis estatico mas alla de sintaxis (pyflakes/pylint,
no confirmados instalados -- se evaluaria igual que pytest, solo si
ya estan disponibles); Fase 11 (Voz) en adelante hasta Fase 16;
decision sobre la arquitectura de agentes duplicada (Fase 6); decidir
cuando conectar RAG (Fase 8) al flujo de Brain; commits/push reales
pendientes de mecanismo de confirmacion humana (Fase 9).
