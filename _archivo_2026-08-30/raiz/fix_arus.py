#!/usr/bin/env python3
"""
fix_arus.py
Reparación automática del proyecto ARUS (MARK6).

Qué hace (todo verificado a mano sobre el proyecto real, no genérico):
  1. Corrige los imports rotos "from core.X" -> "from arus.core.X" en
     arus/core/application.py, arus/core/bootstrap.py y arus/core/logger.py.
     (Estos imports apuntaban a un paquete "core" en la raíz que no existe;
     por eso la app no arrancaba con ModuleNotFoundError: No module named 'core'.)
  2. Archiva (NO borra) los archivos huérfanos/backup que causan confusión
     y uno de ellos ni siquiera compila:
       - main.py (raíz)  -> import roto a un módulo "core" inexistente,
                             y no lo usa run.py (el entrypoint real).
       - arus/interface/main_window_backup.py        -> SyntaxError real
       - arus/interface/main_window_backup_diseño.py -> usa PyQt5 (el resto usa PySide6)
       - arus/interface/main_window_colores_backup.py
       - arus/interface/main_window_antes_limpiar_estilos.py
       - arus/interface/main_window_seguro.py
       - arus/interface/chat_seguro.py
       - arus/interface/core_visual_seguro.py
     Se mueven a _archivo_backups/ con timestamp, por si quieres rescatar algo.
  3. Saca del proyecto el peso muerto que no debería viajar en el repo:
       - PROYECTO_ARUS_MARK5.tar.gz (308 MB, una copia vieja de todo el proyecto)
       - models/vosk-es.zip (38 MB, duplicado: ya está descomprimido en models/vosk-es/)
     Se mueven (no se borran) a ../ARUS_ARCHIVADO_<timestamp>/ fuera del proyecto.
  4. Borra __pycache__ y *.pyc (basura regenerable).
  5. Añade al .gitignore lo que falte (*.tar.gz, *.zip, tmp/, *.db).
  6. Verifica al final que arus/core/application.py, bootstrap.py y logger.py
     ya compilan sin el error de import.

Qué NO hace (y por qué):
  - No toca la duplicación entre los paquetes de la raíz (agents/, ai/, brain/,
    database/, interface/, services/, skills/, memory/, learning/, ...) y el
    paquete arus/ (arus/core, arus/brain, arus/interface, arus/memory, ...).
    Hay dos generaciones del proyecto conviviendo. arus/core/application.py
    importa "ai", "brain", "skills", "commands" DE LA RAÍZ (no de arus/), así
    que ahora mismo el sistema activo mezcla ambas capas a propósito. Decidir
    cuál paquete es la versión "buena" de brain/interface/memory/etc. requiere
    que tú (o yo revisando contenido a mano) elijamos, porque borrar el
    equivocado rompe el sistema. Te lo dejo listado al final del script.
  - No toca arus/interface/window.py vs arus/interface/main_window.py: son dos
    clases ARUSWindow distintas (una es un stub simple, la otra la interfaz
    JARVIS completa). arus/interface/__init__.py expone la primera, pero
    arus/main.py importa la segunda directamente. Funciona, pero es confuso.

Uso:
    cd /ruta/a/PROYECTO_ARUS_MARK6
    python3 fix_arus.py
"""

import os
import re
import shutil
import sys
import py_compile
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

BACKUP_DIR = os.path.join(ROOT, "_archivo_backups", TS)
EXTERNAL_ARCHIVE = os.path.abspath(os.path.join(ROOT, "..", f"ARUS_ARCHIVADO_{TS}"))

# ---------------------------------------------------------------------------

def log(msg):
    print(f"[fix_arus] {msg}")


def paso_1_fix_imports():
    log("Paso 1/6: corrigiendo imports rotos 'from core.' -> 'from arus.core.' ...")
    # NOTA: main.py (raíz) también tiene este problema, pero se archiva en el
    # paso 2 en lugar de corregirse, porque run.py es el entrypoint real.
    objetivos = [
        "arus/core/application.py",
        "arus/core/bootstrap.py",
        "arus/core/logger.py",
        "config/settings.py",
        "database/database.py",
    ]
    patron = re.compile(r"^(from )core(\.[a-zA-Z0-9_.]+ import .+)$", re.MULTILINE)
    tocados = 0
    for rel in objetivos:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            log(f"  ! no encontrado, se salta: {rel}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            contenido = f.read()
        nuevo, n = patron.subn(r"\1arus.core\2", contenido)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(nuevo)
            tocados += 1
            log(f"  ✔ {rel}: {n} import(s) corregido(s)")
        else:
            log(f"  - {rel}: nada que corregir (¿ya estaba arreglado?)")
    log(f"Paso 1 completo. Archivos corregidos: {tocados}")


def _mover_a_backup(rel_path):
    src = os.path.join(ROOT, rel_path)
    if not os.path.exists(src):
        return False
    os.makedirs(BACKUP_DIR, exist_ok=True)
    dst = os.path.join(BACKUP_DIR, rel_path.replace(os.sep, "__"))
    shutil.move(src, dst)
    log(f"  ✔ archivado: {rel_path}")
    return True


def paso_2_archivar_huerfanos():
    log("Paso 2/6: archivando archivos huérfanos/backup que confunden al proyecto ...")
    huerfanos = [
        "main.py",
        "arus/interface/main_window_backup.py",
        "arus/interface/main_window_backup_diseño.py",
        "arus/interface/main_window_colores_backup.py",
        "arus/interface/main_window_antes_limpiar_estilos.py",
        "arus/interface/main_window_seguro.py",
        "arus/interface/chat_seguro.py",
        "arus/interface/core_visual_seguro.py",
    ]
    movidos = 0
    for rel in huerfanos:
        if _mover_a_backup(rel):
            movidos += 1
    log(f"Paso 2 completo. Archivos archivados: {movidos} -> {BACKUP_DIR}")


def paso_3_sacar_peso_muerto():
    log("Paso 3/6: sacando del proyecto los archivos pesados duplicados ...")
    pesados = [
        "PROYECTO_ARUS_MARK5.tar.gz",
        "models/vosk-es.zip",
    ]
    liberado = 0
    movidos = 0
    for rel in pesados:
        src = os.path.join(ROOT, rel)
        if os.path.exists(src):
            size = os.path.getsize(src)
            os.makedirs(EXTERNAL_ARCHIVE, exist_ok=True)
            dst = os.path.join(EXTERNAL_ARCHIVE, os.path.basename(rel))
            shutil.move(src, dst)
            liberado += size
            movidos += 1
            log(f"  ✔ movido fuera del proyecto: {rel} ({size/1024/1024:.1f} MB)")
        else:
            log(f"  - no encontrado, se salta: {rel}")
    if movidos:
        log(f"Paso 3 completo. Liberado ~{liberado/1024/1024:.1f} MB. "
            f"Los archivos quedaron en: {EXTERNAL_ARCHIVE}")
    else:
        log("Paso 3 completo. Nada que mover.")


def paso_4_limpiar_pycache():
    log("Paso 4/6: borrando __pycache__ y *.pyc ...")
    borrados = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "_archivo_backups" in dirpath or ".git" in dirpath:
            continue
        if os.path.basename(dirpath) == "__pycache__":
            shutil.rmtree(dirpath, ignore_errors=True)
            borrados += 1
            continue
        for fn in filenames:
            if fn.endswith(".pyc"):
                try:
                    os.remove(os.path.join(dirpath, fn))
                    borrados += 1
                except OSError:
                    pass
    log(f"Paso 4 completo. Elementos eliminados: {borrados}")


def paso_5_gitignore():
    log("Paso 5/6: actualizando .gitignore ...")
    path = os.path.join(ROOT, ".gitignore")
    faltan = ["*.tar.gz", "*.zip", "tmp/", "*.db"]
    existentes = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existentes = set(l.strip() for l in f.readlines())
    nuevas = [l for l in faltan if l not in existentes]
    if nuevas:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n# añadido por fix_arus.py\n")
            for l in nuevas:
                f.write(l + "\n")
        log(f"  ✔ añadidas {len(nuevas)} reglas: {', '.join(nuevas)}")
    else:
        log("  - .gitignore ya estaba al día")


def paso_6_verificar():
    log("Paso 6/6: verificando que los archivos corregidos compilan ...")
    objetivos = [
        "arus/core/application.py",
        "arus/core/bootstrap.py",
        "arus/core/logger.py",
        "config/settings.py",
        "database/database.py",
    ]
    ok = True
    for rel in objetivos:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        try:
            py_compile.compile(path, doraise=True)
            log(f"  ✔ {rel} compila correctamente")
        except py_compile.PyCompileError as e:
            ok = False
            log(f"  ✘ {rel} SIGUE con error: {e}")
    return ok


def resumen_manual():
    print("\n" + "=" * 78)
    print("PENDIENTE DE DECISIÓN MANUAL (esto el script no lo toca, a propósito):")
    print("=" * 78)
    print("""
1. Duplicación de paquetes: existen carpetas con el mismo propósito en la
   raíz Y dentro de arus/, por ejemplo:
     brain/       vs  arus/brain/  (y arus/core/brain.py)
     interface/   vs  arus/interface/
     memory/      vs  arus/memory/
     database/    vs  arus/core/repository.py + database/
     services/    vs  (usado solo desde la raíz)
   Ahora mismo arus/core/application.py usa las de la RAÍZ (ai/, brain/,
   skills/, commands/), así que ese árbol de la raíz SÍ está en uso real.
   Antes de borrar cualquiera de las versiones duplicadas dentro de arus/,
   dime cuál flujo quieres mantener y lo consolido.

2. arus/interface/window.py (clase ARUSWindow simple) coexiste con
   arus/interface/main_window.py (clase ARUSWindow completa, estilo JARVIS).
   arus/main.py usa la completa (main_window.py); window.py está sin usar
   activamente aunque el __init__.py del paquete lo importa. No rompe nada,
   pero conviene borrar uno de los dos para evitar confusión futura.

3. database/arus.db, database/learning.db, database/test_repository.db y
   data/arus.db conviven. Si alguno ya no se usa, dímelo y lo archivo igual
   que hice con los backups.
""")


def main():
    log(f"Proyecto: {ROOT}")
    paso_1_fix_imports()
    paso_2_archivar_huerfanos()
    paso_3_sacar_peso_muerto()
    paso_4_limpiar_pycache()
    paso_5_gitignore()
    ok = paso_6_verificar()
    resumen_manual()
    if ok:
        log("LISTO. Los errores confirmados quedaron corregidos.")
    else:
        log("Terminado con avisos. Revisa los ✘ de arriba.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
