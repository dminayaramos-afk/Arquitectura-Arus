#!/usr/bin/env python3
"""
fix_arus_v2.py
Limpieza y corrección automática de PROYECTO_ARUS_MARK7.

Este script continúa donde quedó fix_arus.py (imports rotos ya corregidos
en la sesión anterior). Ahora se enfoca en lo que pediste: eliminar
duplicados que generan confusión y dejar solo el código que el sistema
usa de verdad.

CÓMO SÉ QUÉ ES "DUPLICADO MUERTO" Y QUÉ NO:
Rastreé, archivo por archivo, la cadena real de arranque:
  run.py -> arus/main.py -> arus.interface.main_window.ARUSWindow
main_window.py importa: arus.interface.{core_visual,chat,controller,adaptive},
arus.devices.profile, arus.core.voice.
arus.interface.controller importa, a su vez: brain.brain.Brain,
commands.command_manager.CommandManager, skills.skill_manager.SkillManager
(los tres de la RAÍZ del proyecto, no de arus/).

Con un grep de "quién importa esto desde fuera de sí mismo" sobre TODO el
proyecto, confirmé qué carpetas de arus/ nunca las usa nadie: son restos de
fases anteriores (arus/brain, arus/memory, arus/learning, arus/security,
arus/decision, arus/hardware, arus/improvement, arus/installation,
arus/network, arus/orchestration, arus/runtime, arus/system, arus/identity.py,
arus/intelligence/, arus/core_controller.py, y dentro de arus/core/ los
archivos application.py, bootstrap.py, mk1_core.py, admin_panel.py,
automation.py, autonomous_learning.py, health.py, agents.py, core.py,
repository.py, visual_memory.py, logging_config.py, constants.py).
Ninguno de esos aparece en la cadena real de arranque.

Lo que SÍ se queda porque está en uso comprobado:
  - arus/core/{logger.py, paths.py, voice.py}
  - arus/interface/* (la interfaz activa)
  - arus/devices/*
  - arus/laboratory/* (lo usan los tests)
  - todos los paquetes de la RAÍZ (brain/, ai/, agents/, skills/, commands/,
    database/, memory/, security/, services/, learning/, config/)

Qué hace, en orden:
  1. Vuelve a pasar el fix de imports rotos "from core." -> "from arus.core."
     (por si algún archivo nuevo lo trae; en main.py ya no debería hacer falta).
  2. Archiva (NO borra) los subpaquetes de arus/ confirmados como muertos,
     más brain/brain_backup_fase4.py, más probar_arus.py (solo prueba el
     mk1_core que también se archiva), más la carpeta interface/ de la raíz
     (está vacía, es un resto de la reorganización anterior).
  3. Archiva las bases de datos huérfanas: database/arus.db y
     database/learning.db (la base real que usa el sistema es data/arus.db,
     vía arus/core/paths.py -> DATA_DIR). database/test_repository.db NO se
     toca porque los tests sí la referencian.
  4. Saca del proyecto los .tar.gz pesados que quedaron adentro (incluido
     PROYECTO_ARUS_MARK7.tar.gz, una copia de más de 100 MB del propio
     proyecto empaquetada dentro de sí mismo) y el vosk-es.zip duplicado
     si sigue estando.
  5. Limpia __pycache__ y *.pyc.
  6. Actualiza .gitignore.
  7. Verifica que los archivos "vivos" siguen compilando después de todo
     el movimiento.

Al final imprime un aviso sobre el .git pesado (79 MB en tu copia): eso NO
se toca automáticamente porque reescribir el historial de git es
irreversible si no sabes lo que hace; te dejo el comando por si lo quieres
correr tú mismo.

Uso:
    cd /ruta/a/tu/proyecto  (donde está run.py)
    python3 fix_arus_v2.py
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


def log(msg):
    print(f"[fix_arus_v2] {msg}")


def paso_1_fix_imports():
    log("Paso 1/7: revisando imports 'from core.' sueltos (por si quedó alguno nuevo) ...")
    patron = re.compile(r"^(from )core(\.[a-zA-Z0-9_.]+ import .+)$", re.MULTILINE)
    tocados = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if any(p in dirpath for p in (".git", "_archivo_backups", "__pycache__")):
            continue
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    contenido = f.read()
            except (UnicodeDecodeError, OSError):
                continue
            nuevo, n = patron.subn(r"\1arus.core\2", contenido)
            if n:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(nuevo)
                tocados += 1
                log(f"  ✔ {os.path.relpath(path, ROOT)}: {n} import(s) corregido(s)")
    log(f"Paso 1 completo. Archivos corregidos ahora: {tocados}")


def _archivar(rel_path):
    src = os.path.join(ROOT, rel_path)
    if not os.path.exists(src):
        return False
    os.makedirs(BACKUP_DIR, exist_ok=True)
    dst = os.path.join(BACKUP_DIR, rel_path.replace(os.sep, "__"))
    shutil.move(src, dst)
    log(f"  ✔ archivado: {rel_path}")
    return True


def paso_2_archivar_muertos():
    log("Paso 2/7: archivando código muerto (paquetes de arus/ sin ningún uso real) ...")
    muertos = [
        # subpaquetes completos de arus/ sin importadores reales
        "arus/brain",
        "arus/memory",
        "arus/learning",
        "arus/security",
        "arus/decision",
        "arus/hardware",
        "arus/improvement",
        "arus/installation",
        "arus/network",
        "arus/orchestration",
        "arus/runtime",
        "arus/system",
        "arus/intelligence",
        # archivos sueltos sin importadores reales
        "arus/identity.py",
        "arus/core_controller.py",
        # archivos de arus/core/ que nadie usa (se conservan logger.py,
        # paths.py y voice.py porque sí están en uso)
        "arus/core/application.py",
        "arus/core/bootstrap.py",
        "arus/core/mk1_core.py",
        "arus/core/admin_panel.py",
        "arus/core/automation.py",
        "arus/core/autonomous_learning.py",
        "arus/core/health.py",
        "arus/core/agents.py",
        "arus/core/core.py",
        "arus/core/repository.py",
        "arus/core/visual_memory.py",
        "arus/core/logging_config.py",
        "arus/core/constants.py",
        # script de prueba del mk1_core (que se acaba de archivar) y el backup de brain
        "probar_arus.py",
        "brain/brain_backup_fase4.py",
    ]
    movidos = 0
    for rel in muertos:
        if _archivar(rel):
            movidos += 1

    # carpeta interface/ de la raíz: es un duplicado vacío de arus/interface/
    interface_raiz = os.path.join(ROOT, "interface")
    if os.path.isdir(interface_raiz):
        try:
            tiene_archivos = any(
                os.path.isfile(os.path.join(dp, f))
                for dp, _, fs in os.walk(interface_raiz) for f in fs
            )
        except OSError:
            tiene_archivos = True
        if not tiene_archivos:
            shutil.rmtree(interface_raiz, ignore_errors=True)
            log("  ✔ eliminada carpeta vacía: interface/ (duplicado sin archivos de arus/interface/)")
        else:
            _archivar("interface")
            movidos += 1

    log(f"Paso 2 completo. Elementos archivados: {movidos}")


def paso_3_archivar_db_huerfanas():
    log("Paso 3/7: archivando bases de datos huérfanas (la real es data/arus.db) ...")
    huerfanas = ["database/arus.db", "database/learning.db"]
    movidas = 0
    for rel in huerfanas:
        if _archivar(rel):
            movidas += 1
    log(f"Paso 3 completo. Bases de datos archivadas: {movidas} "
        f"(database/test_repository.db se conserva, la usan los tests)")


def paso_4_sacar_peso_muerto():
    log("Paso 4/7: sacando del proyecto archivos pesados que no deberían viajar ...")
    liberado = 0
    movidos = 0
    candidatos = []
    for fn in os.listdir(ROOT):
        if fn.endswith(".tar.gz") or fn == "vosk-es.zip":
            candidatos.append(fn)
    modelos_zip = os.path.join(ROOT, "models", "vosk-es.zip")
    if os.path.exists(modelos_zip):
        candidatos.append(os.path.join("models", "vosk-es.zip"))

    for rel in candidatos:
        src = os.path.join(ROOT, rel)
        if not os.path.exists(src):
            continue
        size = os.path.getsize(src)
        os.makedirs(EXTERNAL_ARCHIVE, exist_ok=True)
        dst = os.path.join(EXTERNAL_ARCHIVE, os.path.basename(rel))
        shutil.move(src, dst)
        liberado += size
        movidos += 1
        log(f"  ✔ movido fuera del proyecto: {rel} ({size/1024/1024:.1f} MB)")

    if movidos:
        log(f"Paso 4 completo. Liberado ~{liberado/1024/1024:.1f} MB en: {EXTERNAL_ARCHIVE}")
    else:
        log("Paso 4 completo. Nada que mover.")


def paso_5_limpiar_pycache():
    log("Paso 5/7: borrando __pycache__ y *.pyc ...")
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
    log(f"Paso 5 completo. Elementos eliminados: {borrados}")


def paso_6_gitignore():
    log("Paso 6/7: actualizando .gitignore ...")
    path = os.path.join(ROOT, ".gitignore")
    faltan = ["*.tar.gz", "*.zip", "tmp/", "*.db"]
    existentes = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existentes = set(l.strip() for l in f.readlines())
    nuevas = [l for l in faltan if l not in existentes]
    if nuevas:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n# añadido por fix_arus_v2.py\n")
            for l in nuevas:
                f.write(l + "\n")
        log(f"  ✔ añadidas {len(nuevas)} reglas: {', '.join(nuevas)}")
    else:
        log("  - .gitignore ya estaba al día")


def paso_7_verificar():
    log("Paso 7/7: verificando que los archivos en uso real siguen compilando ...")
    objetivos = [
        "run.py",
        "arus/main.py",
        "arus/core/logger.py",
        "arus/core/paths.py",
        "arus/core/voice.py",
        "arus/interface/main_window.py",
        "arus/interface/controller.py",
        "arus/interface/core_visual.py",
        "arus/interface/chat.py",
        "arus/interface/adaptive.py",
        "arus/devices/profile.py",
        "config/settings.py",
        "database/database.py",
        "brain/brain.py",
    ]
    ok = True
    for rel in objetivos:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            log(f"  ! no encontrado (revisar): {rel}")
            continue
        try:
            py_compile.compile(path, doraise=True)
            log(f"  ✔ {rel}")
        except py_compile.PyCompileError as e:
            ok = False
            log(f"  ✘ {rel} tiene un error: {e}")
    return ok


def aviso_git():
    print("\n" + "=" * 78)
    print("AVISO (no automatizado a propósito): tu carpeta .git pesa varias")
    print("decenas de MB porque en algún commit anterior quedó guardado el")
    print("tar.gz grande o el modelo de voz. Sacarlo del working directory (lo")
    print("que hace este script) no reduce el historial de git. Si quieres")
    print("reducirlo de verdad, con el proyecto en un estado que te sirva:")
    print("""
    git gc --aggressive --prune=now
""")
    print("Eso limpia objetos sueltos, pero si el archivo pesado sigue en un")
    print("commit viejo del historial, para sacarlo de ahí hace falta reescribir")
    print("el historial (git filter-repo o BFG Repo-Cleaner). Solo hazlo si el")
    print("repo no está compartido con nadie más, porque cambia los hashes de")
    print("todos los commits. Dímelo si quieres que te arme ese paso aparte.")


def main():
    log(f"Proyecto: {ROOT}")
    paso_1_fix_imports()
    paso_2_archivar_muertos()
    paso_3_archivar_db_huerfanas()
    paso_4_sacar_peso_muerto()
    paso_5_limpiar_pycache()
    paso_6_gitignore()
    ok = paso_7_verificar()
    aviso_git()
    if ok:
        log("LISTO. El proyecto quedó limpio y lo que está en uso compila bien.")
    else:
        log("Terminado con avisos. Revisa los ✘ de arriba antes de correr la app.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
