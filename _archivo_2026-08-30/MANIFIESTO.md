# Limpieza 2026-08-30

Archivos movidos aquí (NO borrados) tras confirmar con grep/py_compile que
ningún archivo vivo del proyecto los importa ni los ejecuta. Nada de esto
se ha eliminado permanentemente: si algo falta, está en esta carpeta.

## raiz/

- Basura de comandos de shell mal ejecutados: `0`, `12288`, `28672`, `=`,
  `tatus --short` (0 bytes o un `git diff` volcado por error a un fichero
  con ese nombre).
- Los 18 archivos que la sesión MARK9 ya había marcado como movidos en
  `archivos_movidos_a_archivo_raiz_mark9.txt` pero que en este zip seguían
  presentes en la raíz sin usarse: fix_arus.py, fix_arus_v2.py,
  interfaz.py, main_window_backup.py, main_window_respaldo.py,
  reparar_arus.py, test_brain.py, probar_canales.py, probar_canales2.py,
  probar_vosk.py, completar_fase2.py, finalizar_fase2.py,
  integrar_fase2.py, integrar_fase2_real.py, integrar_fase2_real_v2.py,
  _backup_antes_fase6_brain.py, _backup_antes_fase7_brain.py,
  _backup_antes_fix_fase6_toolagent.py.
- `main_window.py` de la raíz: **copia huérfana, nada la importa.** El
  punto de entrada real (`arus/main.py`) usa
  `arus.interface.main_window`, no este archivo. Coincide (salvo el
  nombre del modelo y la ruta de ollama) con `arus/interface/main_window.py`
  antes de esta limpieza — es una copia vieja abandonada tras una
  restauración fallida del 14/08. El `main_window.py` que subiste suelto
  en este chat es idéntico a esta copia, así que también quedó cubierto.
- Variantes `.bak`/`.antes_*`/`.backup_*` de ese mismo main_window.py
  huérfano.
- Variantes `.backup_copy_text_*`/`.backup_integracion_*`/`.roto_*` de
  `chat_widget.py` (el `chat_widget.py` real y vivo se queda en su sitio).
- `DemoProyecto/` (solo tenía un README.md, sin código).
- `autorepair/` (repair_manager.py sin ninguna referencia en el proyecto).
- `context_tests/` (test suelto y duplicado, ya cubierto por `tests/`).

## arus_interface/

Todo esto vivía dentro de `arus/interface/` mezclado con los archivos
reales, y ninguno lo importa nada del proyecto:

- `e.py` — otra versión huérfana completa de `ARUSWindow` (usaba
  `arus.interface.chat.ChatWidget` en vez del `chat_widget.py` real).
- `window.py` — prototipo antiguo minúsculo de `ARUSWindow`, muy anterior
  al actual.
- `states.py` — constantes `ARUSState` sin ningún uso.
- `chat.py` — versión de `ChatWidget` (85 líneas) distinta y más antigua
  que el `chat_widget.py` real (463 líneas); solo la usaban `e.py` y
  `finalizar_fase2.py`, ambos ya archivados.
- Las 6 variantes `.bak`/`.antes_*`/`.roto_*` del propio
  `main_window.py` real, restos de la misma restauración fallida del
  14/08.

## Verificación hecha antes de mover cualquier cosa

- `grep` de cada nombre de módulo/archivo contra todo el código vivo
  (excluyendo carpetas `_backup_*` y `ARUS_BACKUP`), confirmando cero
  referencias reales (imports, ni siquiera menciones en strings).
- `python3 -m py_compile` sobre todo el árbol vivo antes y después de la
  limpieza: 0 errores de sintaxis.
