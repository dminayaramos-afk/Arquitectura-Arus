# ARUS — Limpieza, optimización y conexión (2026-08-30)

Todo lo aquí descrito está verificado de verdad: `py_compile` sobre todo
el árbol, importación real de la cadena de arranque con PySide6 instalado
(`from arus.interface.main_window import ARUSWindow`), instanciación real
de `ARUSWindow()` en modo offscreen sin excepciones, `pytest` (16/16 OK),
`test_tools.py` (13/13 OK) y `evaluation/suite.py` de la Fase 16
(27/27 OK, 0 fallos, 4 SKIP honestos por red restringida — igual que en
la sesión MARK9 anterior).

## ⚠️ Lo más importante: un bug que se habría colado

Al archivar los huérfanos de `arus/interface/` (`e.py`, `window.py`,
`states.py`, `chat.py` — nada del proyecto vivo los usaba), descubrí que
`arus/interface/__init__.py` SÍ importaba `.window` y `.states`. Python
ejecuta el `__init__.py` de un paquete al cargar cualquiera de sus
submódulos, así que archivar esos dos archivos sin arreglar el
`__init__.py` habría **roto el arranque completo de ARUS** (justo lo que
me pediste evitar). Lo detecté con una verificación cruzada antes de dar
nada por bueno, así que nunca llegó a romperse en un entregable. Lo
arreglé apuntando el `__init__.py` a los módulos reales
(`main_window.ARUSWindow`, `core_visual.NeuralCore`).

## Confirmado con grep antes de tocar nada: `main_window.py` de la raíz es un huérfano

El punto de entrada real (`arus/main.py`) hace
`from arus.interface.main_window import ARUSWindow` — **no** usa el
`main_window.py` de la raíz del proyecto. Ese archivo (idéntico al que
subiste suelto en el chat, salvo el nombre del modelo y la ruta de
ollama) no lo importa nada. Es una copia abandonada de una restauración
fallida del 14 de agosto. Movida a `_archivo_2026-08-30/`, no borrada.

## Código muerto eliminado del `main_window.py` VIVO

Dentro de `arus/interface/main_window.py` (el real) había tres métodos
(`procesar_con_ia`, `buscar_en_web`, `guardar_mensaje_actual`) que
llamaban a Ollama directamente con un prompt hardcodeado sobre política
sudamericana — resto de antes de la Fase 4, cuando arreglaste que el chat
ignorara al `controller`. Confirmé con grep que **nada los llama** (el
chat real va por `chat_widget.py` → `controller.py` → `Brain`, intacto) y
los quité. Backup del archivo completo antes de tocarlo en
`_backup_antes_limpieza_20260830/main_window.py.antes_limpieza`.

## Bug real corregido: arranque de Ollama dependía ciegamente del PATH

`iniciar_ollama_automatico()` (esta sí se ejecuta siempre, al abrir la
app) lanzaba `["ollama", "serve"]` a secas. En los archivos huérfanos
encontré evidencia de que en algún momento tuviste que apuntar a una ruta
absoluta (`/home/damian/ARUS_OLLAMA/bin/bin/ollama`) — probablemente
porque `ollama` no está en tu PATH. Como esa corrección quedó en el
archivo muerto, la interfaz viva nunca se benefició de ella. Ahora:

1. Si defines la variable de entorno `ARUS_OLLAMA_PATH`, se usa esa ruta.
2. Si no, busca `ollama` en el PATH con `shutil.which`.
3. Si tampoco lo encuentra, imprime un mensaje claro en vez de fallar en
   silencio.

Si `ollama` sigue sin estar en tu PATH, exporta antes de lanzar ARUS:

```bash
export ARUS_OLLAMA_PATH="/ruta/real/a/tu/ollama"
```

## Otro bug corregido: script de arranque automático apuntaba a un archivo que no existe

`iniciar_arus_automatico.sh` llamaba a `python3 main.py`, pero no hay
ningún `main.py` en la raíz (solo `run.py`, que sí existe y que a su vez
llama a `arus/main.py`). Corregido a `python3 run.py`.

## Limpieza (archivar, no borrar)

Todo lo identificado como muerto se movió a `_archivo_2026-08-30/`
(con manifiesto detallado dentro) en vez de borrarse:

- Basura de comandos de shell mal ejecutados en la raíz (ficheros de 0
  bytes con nombres como `0`, `12288`, `28672`, `=`, y un `git diff`
  volcado por error a un archivo llamado `tatus --short`).
- Los 18 archivos que la sesión MARK9 ya había marcado como "movidos"
  en `archivos_movidos_a_archivo_raiz_mark9.txt` pero que en este zip
  seguían sin moverse de verdad.
- El `main_window.py` huérfano de la raíz y todas sus variantes `.bak`.
- Variantes `.backup_*`/`.roto_*` de `chat_widget.py` (el real se queda).
- `DemoProyecto/` (solo un README vacío), `autorepair/` (sin ninguna
  referencia), `context_tests/` (duplicado viejo de `tests/`).
- Dentro de `arus/interface/`: `e.py`, `window.py`, `states.py`,
  `chat.py` y 6 variantes `.bak` de `main_window.py`.

`arus/interface/` quedó con exactamente lo que se usa:
`__init__.py`, `main_window.py`, `controller.py`, `core_visual.py`,
`adaptive.py`.

## No incluido en este zip (sin cambios, ya lo tienes)

- `_backup_antes_fase*/`, `_backup_fase*/`, `ARUS_BACKUP/` — backups
  históricos, no tocados, no reenviados (pesan ~200 MB en total y no han
  cambiado).
- `models/vosk-es/` (58 MB, modelo de voz Vosk) — sin cambios.

**Aviso aparte:** `_backup_antes_fase4/` pesa 175 MB porque contiene
**tres copias duplicadas** de una carpeta `models/` de 58 MB cada una
(quedó atrapada en tres snapshots históricos de aquella fase). No lo he
tocado porque sigue tu política de no tocar backups, pero si algún día
quieres liberar espacio en disco, ahí tienes ~115 MB de duplicados
seguros de borrar.

## Cosas que audité y dejé exactamente como estaban (decisiones tuyas)

- `arus/laboratory/` — un subsistema entero de 228 KB (agentes,
  repositorios, runtime, multimedia) con sus propios tests, pero
  **completamente desconectado** del núcleo: nada en `brain/`,
  `controller.py` ni `main_window.py` lo importa. No sabía si es trabajo
  en curso que quieres seguir desarrollando aparte o algo para archivar,
  así que no lo toqué. Es la pieza más grande de "código sin conectar"
  que queda en el proyecto.
- `verification/` y `planning/` — siguen huérfanos, como ya sabías
  (decisión pendiente #10 de la sesión MARK9).

## Cómo aplicar esto a tu repo

```bash
cd ~/ruta/a/tu/proyecto/ARUS
unzip ~/Descargas/ARUS_limpieza_2026-08-30.zip -d /tmp/arus_nuevo
# Copia el contenido actualizado sobre tu proyecto real
cp -r /tmp/arus_nuevo/Arquitectura-Arus-main/. .
rm -rf /tmp/arus_nuevo

python3 run.py   # o iniciar_arus_automatico.sh, ya corregido
```

Tus carpetas `_backup_*`, `ARUS_BACKUP` y `models/` no vienen en este zip
porque no cambiaron — se quedan tal cual las tengas en tu máquina.
