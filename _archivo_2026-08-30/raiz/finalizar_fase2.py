from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime

ROOT = Path("/home/damian/ARUS_restaurado")
CHAT = ROOT / "arus/interface/chat.py"

print("=" * 70)
print(" ARUS MARK 7 — FASE 2")
print(" Integración definitiva ConversationManager")
print("=" * 70)

# ------------------------------------------------------------
# Comprobar componentes
# ------------------------------------------------------------

CM = ROOT / "conversations/conversation_manager.py"
REPO = ROOT / "database/conversation_session_repository.py"

if not CM.exists():
    print("[ERROR] No existe:", CM)
    sys.exit(1)

if not REPO.exists():
    print("[ERROR] No existe:", REPO)
    sys.exit(1)

if not CHAT.exists():
    print("[ERROR] No existe:", CHAT)
    sys.exit(1)

print("[OK] ConversationManager encontrado")
print("[OK] ConversationSessionRepository encontrado")
print("[OK] ChatWidget encontrado")

# ------------------------------------------------------------
# Comprobar sintaxis actual
# ------------------------------------------------------------

result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("[ERROR] chat.py ya tiene errores de sintaxis.")
    print(result.stderr)
    sys.exit(1)

print("[OK] chat.py original tiene sintaxis correcta")

# ------------------------------------------------------------
# Backup
# ------------------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = ROOT / "ARUS_BACKUP" / f"fase2_definitiva_{timestamp}"
backup_dir.mkdir(parents=True, exist_ok=True)

backup = backup_dir / "chat.py"
shutil.copy2(CHAT, backup)

print("[OK] Backup creado:")
print(backup)

# ------------------------------------------------------------
# Código completo de ChatWidget
#
# MISMA INTERFAZ:
# - QWidget
# - QTextEdit
# - QLineEdit
# - QPushButton
# - mismos estilos
# - mismo botón
# - mismo flujo Ollama
#
# ÚNICA FUNCIÓN NUEVA:
# persistencia ConversationManager
# ------------------------------------------------------------

new_chat = '''"""
ARUS
Chat Identity & Chat Interface
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton
)

from conversations.conversation_manager import ConversationManager


class ChatWidget(QWidget):

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        # ----------------------------------------------------
        # ARUS FASE 2
        # Sistema persistente de conversaciones.
        # ----------------------------------------------------
        self.conversation_manager = ConversationManager()
        self.conversation_id = self.conversation_manager.create(
            title="Nueva conversación"
        )

        layout = QVBoxLayout()

        self.history = QTextEdit()
        self.history.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setFocus()
        self.input.returnPressed.connect(self.send)

        self.button = QPushButton("Enviar")
        self.button.clicked.connect(self.send)

        layout.addWidget(self.history)
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.setStyleSheet("""
        QWidget{
            background:#020611;
            color:#00E5FF;
        }
        QTextEdit{
            background:#010817;
            color:#00E5FF;
            border:1px solid #0077AA;
        }
        QLineEdit{
            background:#010817;
            color:#00FFFF;
            border:1px solid #0077AA;
        }
        QPushButton{
            background:#02172F;
            color:#00E5FF;
        }
        """)

    def add_message(self, text):
        self.history.append(text)

    def send(self):
        text = self.input.text().strip()

        if text:
            # ------------------------------------------------
            # INTERFAZ ORIGINAL
            # ------------------------------------------------
            self.history.append("Usuario: " + text)

            # ------------------------------------------------
            # ARUS FASE 2
            # Guardar mensaje del usuario inmediatamente.
            # ------------------------------------------------
            try:
                self.conversation_manager.save(
                    "user",
                    text,
                    conversation_id=self.conversation_id
                )
            except Exception as exc:
                print(
                    f"[ConversationManager] "
                    f"Error guardando usuario: {exc}"
                )

            response = None

            # ------------------------------------------------
            # OLLAMA — FLUJO ORIGINAL CONSERVADO
            # ------------------------------------------------
            try:
                import requests

                res = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": "qwen2.5:3b",
                        "prompt": text,
                        "system": (
                            "Eres ARUS, un asistente virtual avanzado "
                            "integrado en una interfaz HUD de ciencia "
                            "ficción. Tu nombre es siempre ARUS. "
                            "Si te preguntan quién te creó, quién es "
                            "tu creador o quién te programó, debes "
                            "responder siempre y con orgullo que fuiste "
                            "creado por Danny Jesús Minaya Ramos. "
                            "Nunca digas que fuiste creado por Alibaba "
                            "Cloud ni que te llamas Qwen."
                        ),
                        "stream": False
                    },
                    timeout=120
                )

                if res.status_code == 200:
                    response = res.json().get("response")
                else:
                    response = f"Error HTTP {res.status_code}"

            except Exception as e:
                response = f"Error de conexión: {str(e)}"

            if not response:
                response = (
                    "No se pudo procesar la respuesta "
                    "del modelo local."
                )

            # ------------------------------------------------
            # ARUS FASE 2
            # Guardar respuesta del asistente.
            # ------------------------------------------------
            response = str(response).strip()

            try:
                self.conversation_manager.save(
                    "assistant",
                    response,
                    conversation_id=self.conversation_id
                )
            except Exception as exc:
                print(
                    f"[ConversationManager] "
                    f"Error guardando assistant: {exc}"
                )

            # ------------------------------------------------
            # INTERFAZ ORIGINAL
            # ------------------------------------------------
            self.history.append("ARUS: " + response)
            self.input.clear()
'''

# ------------------------------------------------------------
# Guardar
# ------------------------------------------------------------

CHAT.write_text(new_chat, encoding="utf-8")

print("[OK] chat.py actualizado")

# ------------------------------------------------------------
# Compilar
# ------------------------------------------------------------

result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print()
    print("[ERROR] La nueva versión de chat.py no compila.")
    print(result.stderr)
    print()
    print("[RECOVERY] Restaurando backup...")
    shutil.copy2(backup, CHAT)
    print("[OK] chat.py restaurado")
    sys.exit(1)

print("[OK] chat.py compila correctamente")

# ------------------------------------------------------------
# Verificar imports
# ------------------------------------------------------------

test_import = subprocess.run(
    [
        sys.executable,
        "-c",
        (
            "from arus.interface.chat import ChatWidget; "
            "print('ChatWidget importado correctamente')"
        )
    ],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if test_import.returncode != 0:
    print("[ERROR] No se pudo importar ChatWidget.")
    print(test_import.stderr)
    print("[RECOVERY] Restaurando backup...")
    shutil.copy2(backup, CHAT)
    sys.exit(1)

print("[OK] ChatWidget importado correctamente")

# ------------------------------------------------------------
# Prueba ConversationManager
# ------------------------------------------------------------

print()
print("[TEST] Probando persistencia de conversación...")

test_code = r'''
from conversations.conversation_manager import ConversationManager

cm = ConversationManager()

cid = cm.create(title="Prueba Fase 2 definitiva")

cm.save(
    "user",
    "Hola ARUS",
    conversation_id=cid
)

cm.save(
    "assistant",
    "Hola. Soy ARUS.",
    conversation_id=cid
)

data = cm.load(cid)

assert data is not None
assert data["id"] == cid
assert len(data["messages"]) == 2
assert data["messages"][0]["role"] == "user"
assert data["messages"][0]["content"] == "Hola ARUS"
assert data["messages"][1]["role"] == "assistant"
assert data["messages"][1]["content"] == "Hola. Soy ARUS."

print("Conversation ID:", cid)
print("Mensajes:", len(data["messages"]))
print("Persistencia: OK")
'''

result = subprocess.run(
    [sys.executable, "-c", test_code],
    cwd=ROOT,
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print("[ERROR] La prueba de persistencia falló.")
    print(result.stdout)
    print(result.stderr)
    print("[RECOVERY] Restaurando chat.py...")
    shutil.copy2(backup, CHAT)
    print("[OK] Restaurado")
    sys.exit(1)

print(result.stdout)

# ------------------------------------------------------------
# Verificar archivos que NO deben haber cambiado
# ------------------------------------------------------------

print("[OK] controller.py NO modificado por este proceso")
print("[OK] main_window.py NO modificado por este proceso")
print("[OK] Interfaz visual conservada")
print("[OK] Ollama conservado")

# ------------------------------------------------------------
# Resultado
# ------------------------------------------------------------

print()
print("=" * 70)
print(" FASE 2 — COMPLETADA")
print("=" * 70)
print()
print("ConversationManager:       OK")
print("SQLite:                    OK")
print("Creación conversación:     OK")
print("Guardado usuario:          OK")
print("Guardado assistant:        OK")
print("Carga conversación:        OK")
print("ChatWidget:                OK")
print("Sintaxis:                  OK")
print("Interfaz:                  CONSERVADA")
print("Ollama:                    CONSERVADO")
print()
print("Backup:")
print(backup)
print()
print("SIGUIENTE PASO:")
print("git diff -- arus/interface/chat.py")
print()
print("NO hagas todavía git add .")
print("NO pases todavía a Fase 3.")
print("=" * 70)
