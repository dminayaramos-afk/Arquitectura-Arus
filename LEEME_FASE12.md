# ARUS MARK 7 — FASE 12: Visión

## Como instalar
Añade/sustituye (mismas rutas):

    vision/__init__.py           (nuevo)
    vision/image_loader.py       (nuevo)
    vision/vision_provider.py    (nuevo)
    vision/vision_manager.py     (nuevo)
    tools/screenshot_tool.py     (nuevo)
    brain/brain.py               (modificado: expone self.vision)

No se toco `arus/interface/*`.

## Auditoria previa
`arus/laboratory/` tiene un par de Enum (`FileType.IMAGE`,
`MediaType.IMAGE`) pero es codigo sin usar -- solo lo referencian sus
propios tests y el script de limpieza de la Fase 1 (confirmado antes
de escribir nada). No hay carga de imagenes, provider, ni nada que
hable con un modelo de vision. Infraestructura nueva.

## Dos honestidades importantes de esta fase (mas que en RAG)
1. **El modelo configurado (`qwen2.5:3b`) no es multimodal.**
   `OllamaVisionProvider` comprueba de verdad, contra Ollama, si el
   modelo de vision indicado (por defecto `llava`) esta instalado
   antes de intentar usarlo -- si no, lo dice con claridad y te dice
   el comando exacto para instalarlo (`ollama pull llava`), en vez de
   fingir un analisis.
2. **Ni siquiera hay por donde entraria una imagen.** A diferencia de
   RAG (que se puede alimentar con archivos que ya estan en disco),
   tu interfaz no tiene ningun control para subir, arrastrar o pegar
   una imagen. Aunque conectara esto a Brain automaticamente, hoy no
   hay manera de que uses esto desde la GUI. Lo digo claramente en
   vez de fingir que "ya funciona".

## Lo que SI se puede usar ya mismo: ScreenshotTool
Capturar pantalla NO necesita un modelo de vision, solo Pillow (ya
esta instalado en tu proyecto). `tools/screenshot_tool.py` es una
herramienta real que el modelo puede pedir ejecutar ahora mismo a
traves del ciclo de function-calling de la Fase 6 -- guarda la
captura en `tmp/capturas/` y devuelve la ruta. Analizar esa captura
sigue dependiendo de tener un modelo de vision instalado (punto 1 de
arriba).

## Pipeline implementado (punto 26)
    IMAGE -> ImageLoader -> VisionProvider -> ANALYSIS

- `ImageLoader`: valida extension (png/jpg/jpeg/webp/bmp/gif) y
  tamaño (limite 8 MB), convierte a base64.
- `VisionProvider` / `OllamaVisionProvider`: comprueba disponibilidad
  real contra Ollama (`client.list()`), y si el modelo esta, llama a
  `ollama.chat(images=[...])` (el mecanismo real que usa Ollama para
  modelos multimodales).
- `VisionManager`: fachada -- `analyze(image_path, prompt=None)`.

## Por que NO se conecto a Brain.think() automaticamente
Mismo criterio que RAG en la Fase 8, mas la razon 2 de arriba (no hay
entrada de imagen en la GUI). `Brain` expone `self.vision` funcional
y probado, listo para cuando exista un modelo de vision instalado Y
una via real para que el usuario le pase una imagen a ARUS.

## Probado
1. Convertir una imagen PNG real (generada con Pillow) a base64:
   cabecera PNG valida tras decodificar. OK.
2. Un archivo con extension no soportada (.txt) se rechaza con error
   claro. OK.
3. `OllamaVisionProvider.is_available()` devuelve `False` de forma
   honesta (ni Ollama ni el modelo de vision estan instalados en este
   entorno) sin lanzar excepcion. OK.
4. `analyze()` sin modelo disponible: mensaje honesto y accionable
   ("instala con ollama pull llava"), no una descripcion inventada.
   OK.
5. **Camino positivo probado tambien:** simule un Ollama con `llava`
   SI instalado -- `is_available()` devolvio `True` y `analyze()`
   devolvio una respuesta real construida a partir de la imagen
   (confirme que el base64 de la imagen de verdad llega en el campo
   `images` de la llamada). OK.
6. `ScreenshotTool`: en este entorno sin pantalla, falla con un
   mensaje claro ("no hay entorno grafico disponible") en vez de
   reventar con un traceback -- exactamente el comportamiento
   esperado en un servidor sin GUI; en tu maquina con pantalla
   deberia capturar de verdad.
7. `ToolManager` detecta `screenshot` automaticamente; `Brain` expone
   `self.vision` sin romper nada.
8. Sin regresion en Fases 2-11 (chat normal, memoria de nombre).
9. Interfaz identica byte a byte. Sintaxis de todo el proyecto: OK.

## FASE 12 — RESULTADO

Archivos creados:
- vision/__init__.py, vision/image_loader.py, vision/vision_provider.py,
  vision/vision_manager.py
- tools/screenshot_tool.py

Archivos modificados:
- brain/brain.py (expone self.vision; NO conectado al flujo de think())

Archivos NO modificados:
- arus/interface/* (identico byte a byte)
- resto del proyecto

Pruebas: 9 casos reales, incluido el camino positivo simulado con un
modelo de vision instalado. Interfaz visual: sin cambios. Arranque
completo con PySide6/Ollama/un modelo de vision real: NO VERIFICADO
en este entorno (nada de eso esta instalado aqui) — confirmalo en tu
maquina, y solo tendra sentido si instalas un modelo como llava o
qwen2.5vl.

Pendiente: decidir una via real para que el usuario le pase una
imagen a ARUS (necesitaria tocar la interfaz, o un flujo por ruta de
archivo via chat de texto); conectar Vision a Brain.think() cuando
tenga sentido; Fase 13 (Tareas autonomas) en adelante hasta Fase 16;
decisiones pendientes de fases anteriores (agentes duplicados,
cuando conectar RAG, confirmacion humana para Git, STT duplicado,
voz->Brain->voz).
