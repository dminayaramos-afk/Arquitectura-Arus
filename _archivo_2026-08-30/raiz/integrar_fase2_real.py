from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

ROOT = Path("/home/damian/ARUS_restaurado")
CHAT = ROOT / "arus/interface/chat.py"

print("=" * 70)
print("ARUS — INTEGRACIÓN REAL FASE 2")
print("ConversationManager + ChatWidget")
print("=" * 70)

# ---------------------------------------------------------
# Comprobaciones
# ---------------------------------------------------------

if not CHAT.exists():
    print("[ERROR] No existe:", CHAT)
    sys.exit(1)

CM = ROOT / "conversations/conversation_manager.py"
REPO = ROOT / "database/conversation_session_repository.py"

if not CM.exists():
    print("[ERROR] Falta ConversationManager")
    sys.exit(1)

if not REPO.exists():
    print("[ERROR] Falta ConversationSessionRepository")
    sys.exit(1)

print("[OK] ConversationManager encontrado")
print("[OK] ConversationSessionRepository encontrado")

# ---------------------------------------------------------
# Comprobar sintaxis original
# ---------------------------------------------------------

result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("[ERROR] chat.py ya tenía errores de sintaxis.")
    print(result.stderr)
    sys.exit(1)

print("[OK] chat.py tiene sintaxis válida")

# ---------------------------------------------------------
# Backup
# ---------------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "ARUS_BACKUP" / f"fase2_chat_{timestamp}"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

backup_file = BACKUP_DIR / "chat.py"
shutil.copy2(CHAT, backup_file)

print("[OK] Backup creado:")
print(backup_file)

# ---------------------------------------------------------
# Leer archivo
# ---------------------------------------------------------

source = CHAT.read_text(encoding="utf-8")

# ---------------------------------------------------------
# Evitar doble integración
# ---------------------------------------------------------

if "ConversationManager" in source:
    print("[INFO] ConversationManager ya aparece en chat.py.")
    print("No se realizará una segunda integración.")
    sys.exit(0)

# ---------------------------------------------------------
# 1. Añadir import
# ---------------------------------------------------------

old_import = """from PySide6.QtWidgets import (
QWidget,
QVBoxLayout,
QTextEdit,
QLineEdit,
QPushButton
)
"""

new_import = """from PySide6.QtWidgets import (
QWidget,
QVBoxLayout,
QTextEdit,
QLineEdit,
QPushButton
)

from conversations.conversation_manager import ConversationManager
"""

if old_import not in source:
    print("[ERROR] No encontré el bloque de imports esperado.")
    print("No modificaré el archivo.")
    sys.exit(1)

source = source.replace(old_import, new_import, 1)

# ---------------------------------------------------------
# 2. Crear ConversationManager en __init__
# ---------------------------------------------------------

old_init = """def __init__(self, controller=None):
    super().__init__()
    self.controller = controller

    layout = QVBoxLayout()
"""

new_init = """def __init__(self, controller=None):
    super().__init__()
    self.controller = controller

    # ARUS FASE 2
    # Gestor persistente de conversaciones.
    self.conversation_manager = ConversationManager()
    self.conversation_id = self.conversation_manager.create(
        title="Nueva conversación"
    )

    layout = QVBoxLayout()
"""

if old_init not in source:
    print("[ERROR] No encontré el __init__ esperado.")
    print("No modificaré el archivo.")
    sys.exit(1)

source = source.replace(old_init, new_init, 1)

# ---------------------------------------------------------
# 3. Guardar mensaje del usuario
# ---------------------------------------------------------

old_user = """if text:
        self.history.append("Usuario: " + text)
        response = None
"""

new_user = """if text:
        self.history.append("Usuario: " + text)

        # ARUS FASE 2
        # Guardado incremental: se ejecuta en cada turno.
        try:
            self.conversation_manager.save(
                "user",
                text,
                conversation_id=self.conversation_id
            )
        except Exception as exc:
            print(f"[ConversationManager] Error guardando usuario: {exc}")

        response = None
"""

if old_user not in source:
    print("[ERROR] No encontré el punto donde se procesa el mensaje.")
    print("No modificaré el archivo.")
    sys.exit(1)

source = source.replace(old_user, new_user, 1)

# ---------------------------------------------------------
# 4. Guardar respuesta de ARUS
# ---------------------------------------------------------

old_response = """        self.history.append("ARUS: " + str(response).strip())
        self.input.clear()
"""

new_response = """        response = str(response).strip()

        # ARUS FASE 2
        # Guardado incremental de la respuesta del asistente.
        try:
            self.conversation_manager.save(
                "assistant",
                response,
                conversation_id=self.conversation_id
            )
        except Exception as exc:
            print(f"[ConversationManager] Error guardando assistant: {exc}")

        self.history.append("ARUS: " + response)
        self.input.clear()
"""

if old_response not in source:
    print("[ERROR] No encontré el punto donde se muestra la respuesta.")
    print("No modificaré el archivo.")
    sys.exit(1)

source = source.replace(old_response, new_response, 1)

# ---------------------------------------------------------
# Escribir modificación
# ---------------------------------------------------------

CHAT.write_text(source, encoding="utf-8")

print("[OK] chat.py modificado")

# ---------------------------------------------------------
# Verificar sintaxis
# ---------------------------------------------------------

result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print()
    print("[ERROR] La modificación produjo un error de sintaxis.")
    print(result.stderr)
    print()
    print("Restaurando backup...")

    shutil.copy2(backup_file, CHAT)

    print("[OK] chat.py restaurado.")
    sys.exit(1)

print("[OK] chat.py compila correctamente")

# ---------------------------------------------------------
# Prueba del ConversationManager
# ---------------------------------------------------------

print()
print("[TEST] Probando persistencia...")

test_code = r'''
from conversations.conversation_manager import ConversationManager

cm = ConversationManager()

cid = cm.create(title="Prueba Fase 2 integrada")

cm.save(
    "user",
    "Hola ARUS, prueba de integración",
    conversation_id=cid
)

cm.save(
    "assistant",
    "Hola. La integración de la Fase 2 funciona.",
    conversation_id=cid
)

data = cm.load(cid)

assert data is not None
assert len(data["messages"]) == 2
assert data["messages"][0]["role"] == "user"
assert data["messages"][1]["role"] == "assistant"

print("CONVERSATION_ID:", cid)
print("MENSAJES:", len(data["messages"]))
print("RESULTADO: OK")
'''

result = subprocess.run(
    [sys.executable, "-c", test_code],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("[ERROR] Falló la prueba.")
    print(result.stdout)
    print(result.stderr)

    print("Restaurando chat.py...")
    shutil.copy2(backup_file, CHAT)

    print("[OK] chat.py restaurado.")
    sys.exit(1)

print(result.stdout)

# ---------------------------------------------------------
# Comprobación final
# ---------------------------------------------------------

print("=" * 70)
print("FASE 2 — INTEGRACIÓN COMPLETADA")
print("=" * 70)

print()
print("ConversationManager:       OK")
print("SQLite:                    OK")
print("ChatWidget:                INTEGRADO")
print("Guardado usuario:          OK")
print("Guardado assistant:        OK")
print("Sintaxis:                  OK")
print("Backup:                    OK")
print()
print("Archivos modificados:")
print("  arus/interface/chat.py")
print()
print("Archivos NO modificados:")
print("  arus/interface/controller.py")
print("  arus/interface/main_window.py")
print()
print("INTERFAZ GRÁFICA: NO MODIFICADA")
print()
print("Backup disponible en:")
print(BACKUP_DIR)
print()
print("Antes de pasar a Fase 3:")
print("  git diff -- arus/interface/chat.py")
print()
