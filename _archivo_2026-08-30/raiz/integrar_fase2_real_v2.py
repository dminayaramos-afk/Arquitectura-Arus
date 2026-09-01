from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

ROOT = Path("/home/damian/ARUS_restaurado")
CHAT = ROOT / "arus/interface/chat.py"

print("=" * 70)
print(" ARUS — FASE 2 — INTEGRACIÓN SEGURA V2")
print("=" * 70)

# ---------------------------------------------------------
# Comprobaciones
# ---------------------------------------------------------

cm = ROOT / "conversations/conversation_manager.py"
repo = ROOT / "database/conversation_session_repository.py"

if not cm.exists():
    print("[ERROR] Falta conversations/conversation_manager.py")
    sys.exit(1)

if not repo.exists():
    print("[ERROR] Falta database/conversation_session_repository.py")
    sys.exit(1)

if not CHAT.exists():
    print("[ERROR] Falta arus/interface/chat.py")
    sys.exit(1)

print("[OK] Componentes de Fase 2 encontrados")

# ---------------------------------------------------------
# Comprobar sintaxis antes
# ---------------------------------------------------------

result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("[ERROR] chat.py ya contiene un error.")
    print(result.stderr)
    sys.exit(1)

print("[OK] chat.py tiene sintaxis válida")

# ---------------------------------------------------------
# Leer
# ---------------------------------------------------------

source = CHAT.read_text(encoding="utf-8")

if "ConversationManager" in source:
    print("[INFO] ConversationManager ya está presente.")
    print("No se hará una segunda integración.")
    sys.exit(0)

# ---------------------------------------------------------
# Backup
# ---------------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = ROOT / "ARUS_BACKUP" / f"fase2_chat_v2_{timestamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

backup = backup_dir / "chat.py"
shutil.copy2(CHAT, backup)

print("[OK] Backup:")
print(backup)

# ---------------------------------------------------------
# 1. IMPORT
# ---------------------------------------------------------

needle = "from PySide6.QtWidgets import ("

if needle not in source:
    print("[ERROR] No encontré el import de PySide6.")
    print("NO se modificará el archivo.")
    sys.exit(1)

# Encontrar el cierre del bloque de imports
start = source.index(needle)
end = source.index(")", start) + 1

import_block = source[start:end]

new_import_block = (
    import_block
    + "\n\n"
    + "from conversations.conversation_manager import ConversationManager"
)

source = source[:start] + new_import_block + source[end:]

print("[OK] Import de ConversationManager añadido")

# ---------------------------------------------------------
# 2. INIT
# ---------------------------------------------------------

needle_init = "    self.controller = controller"

if needle_init not in source:
    print("[ERROR] No encontré self.controller = controller")
    print("Restaurando.")
    shutil.copy2(backup, CHAT)
    sys.exit(1)

init_code = """
    # ARUS FASE 2 - persistencia de conversaciones
    self.conversation_manager = ConversationManager()
    self.conversation_id = self.conversation_manager.create(
        title="Nueva conversación"
    )
"""

source = source.replace(
    needle_init,
    needle_init + init_code,
    1
)

print("[OK] ConversationManager inicializado")

# ---------------------------------------------------------
# 3. MENSAJE USUARIO
# ---------------------------------------------------------

needle_user = '        self.history.append("Usuario: " + text)'

if needle_user not in source:
    print("[ERROR] No encontré el punto del mensaje del usuario.")
    shutil.copy2(backup, CHAT)
    sys.exit(1)

user_code = """
        
        # ARUS FASE 2 - guardado incremental del usuario
        try:
            self.conversation_manager.save(
                "user",
                text,
                conversation_id=self.conversation_id
            )
        except Exception as exc:
            print(
                f"[ConversationManager] Error guardando usuario: {exc}"
            )
"""

source = source.replace(
    needle_user,
    needle_user + user_code,
    1
)

print("[OK] Guardado de mensajes del usuario integrado")

# ---------------------------------------------------------
# 4. RESPUESTA
# ---------------------------------------------------------

needle_response = '        self.history.append("ARUS: " + str(response).strip())'

if needle_response not in source:
    print("[ERROR] No encontré el punto de respuesta de ARUS.")
    shutil.copy2(backup, CHAT)
    sys.exit(1)

response_code = """
        
        # ARUS FASE 2 - guardado incremental de ARUS
        response = str(response).strip()

        try:
            self.conversation_manager.save(
                "assistant",
                response,
                conversation_id=self.conversation_id
            )
        except Exception as exc:
            print(
                f"[ConversationManager] Error guardando assistant: {exc}"
            )
"""

source = source.replace(
    needle_response,
    response_code + '\n        self.history.append("ARUS: " + response)',
    1
)

print("[OK] Guardado de respuestas de ARUS integrado")

# ---------------------------------------------------------
# 5. Seguridad: NO tocar interfaz
# ---------------------------------------------------------

# Comprobar que no desaparecieron elementos fundamentales.
required = [
    "class ChatWidget(QWidget):",
    "self.history = QTextEdit()",
    "self.input = QLineEdit()",
    'self.button = QPushButton("Enviar")',
    "self.input.returnPressed.connect(self.send)",
    "self.button.clicked.connect(self.send)",
    "self.setStyleSheet",
    "requests.post(",
    "http://127.0.0.1:11434/api/generate",
]

for item in required:
    if item not in source:
        print("[ERROR] Falta elemento protegido:")
        print(item)
        print("Restaurando backup.")
        shutil.copy2(backup, CHAT)
        sys.exit(1)

print("[OK] Elementos de interfaz protegidos intactos")
print("[OK] Ruta de Ollama intacta")

# ---------------------------------------------------------
# 6. Escribir
# ---------------------------------------------------------

CHAT.write_text(source, encoding="utf-8")

print("[OK] chat.py actualizado")

# ---------------------------------------------------------
# 7. Compilar
# ---------------------------------------------------------

result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("[ERROR] Error de sintaxis después de modificar.")
    print(result.stderr)

    print("Restaurando backup...")
    shutil.copy2(backup, CHAT)

    print("[OK] Restaurado.")
    sys.exit(1)

print("[OK] chat.py compila correctamente")

# ---------------------------------------------------------
# 8. Prueba independiente de persistencia
# ---------------------------------------------------------

print()
print("[TEST] Probando ConversationManager...")

test = r'''
from conversations.conversation_manager import ConversationManager

cm = ConversationManager()

cid = cm.create(title="Prueba Fase 2")

cm.save(
    "user",
    "Mensaje de prueba",
    conversation_id=cid
)

cm.save(
    "assistant",
    "Respuesta de prueba",
    conversation_id=cid
)

data = cm.load(cid)

assert data is not None
assert len(data["messages"]) == 2
assert data["messages"][0]["role"] == "user"
assert data["messages"][1]["role"] == "assistant"

print("ID:", cid)
print("Mensajes:", len(data["messages"]))
print("Persistencia: OK")
'''

result = subprocess.run(
    [sys.executable, "-c", test],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("[ERROR] Falló la prueba.")
    print(result.stdout)
    print(result.stderr)

    print("Restaurando chat.py...")
    shutil.copy2(backup, CHAT)
    print("[OK] Restaurado.")
    sys.exit(1)

print(result.stdout)

# ---------------------------------------------------------
# FINAL
# ---------------------------------------------------------

print("=" * 70)
print(" FASE 2 — INTEGRACIÓN COMPLETADA")
print("=" * 70)
print()
print("ConversationManager:       OK")
print("Persistencia SQLite:       OK")
print("Usuario:                   OK")
print("Assistant:                 OK")
print("chat.py:                   OK")
print("Interfaz:                  CONSERVADA")
print("Ollama:                    CONSERVADO")
print("controller.py:             NO TOCADO")
print("main_window.py:            NO TOCADO")
print()
print("Backup:")
print(backup)
print()
print("SIGUIENTE COMPROBACIÓN:")
print("git diff -- arus/interface/chat.py")
print("=" * 70)
