#!/usr/bin/env python3

from __future__ import annotations

import ast
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "_backup_fase2" / STAMP


def log(text):
    print(f"[ARUS] {text}")


def ok(text):
    print(f"[OK]   {text}")


def warn(text):
    print(f"[WARN] {text}")


def fail(text):
    print(f"[FAIL] {text}")


def backup_file(relative):
    source = ROOT / relative

    if not source.exists():
        warn(f"No existe para backup: {relative}")
        return

    target = BACKUP / relative
    target.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source, target)

    ok(f"Backup: {relative}")


def write_file(relative, content):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    ok(f"Escrito: {relative}")


# ================================================================
# ARUS MAIN
# ================================================================

MAIN_PY = '''#!/usr/bin/env python3
"""
ARUS Launcher
"""

from __future__ import annotations

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PySide6.QtWidgets import QApplication
from arus.interface.main_window import ARUSWindow


def main() -> int:
    app = QApplication(sys.argv)

    window = ARUSWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
'''


# ================================================================
# CHAT WIDGET - FASE 2
# ================================================================

CHAT_PY = '''"""
ARUS
Chat Identity & Chat Interface

Fase 2:
- ConversationManager
- Persistencia incremental
- Historial de conversación
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
)

from conversations.conversation_manager import ConversationManager


class ChatWidget(QWidget):

    def __init__(self, controller=None):
        super().__init__()

        self.controller = controller

        # --------------------------------------------------------
        # ConversationManager
        # --------------------------------------------------------

        self.conversation_manager = ConversationManager()

        self.conversation_id = (
            self.conversation_manager.create(
                title="Nueva conversación"
            )
        )

        # --------------------------------------------------------
        # INTERFAZ ORIGINAL
        # --------------------------------------------------------

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
        QWidget {
            background: #020611;
            color: #00E5FF;
        }

        QTextEdit {
            background: #010817;
            color: #00E5FF;
            border: 1px solid #0077AA;
        }

        QLineEdit {
            background: #010817;
            color: #00FFFF;
            border: 1px solid #0077AA;
        }

        QPushButton {
            background: #02172F;
            color: #00E5FF;
        }
        """)

    # ------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------

    def add_message(self, text: str):
        self.history.append(str(text))

    # ------------------------------------------------------------
    # Envío
    # ------------------------------------------------------------

    def send(self):

        text = self.input.text().strip()

        if not text:
            return

        self.history.append(
            "Usuario: " + text
        )

        # --------------------------------------------------------
        # Guardar usuario
        # --------------------------------------------------------

        try:
            self.conversation_manager.save(
                "user",
                text,
                conversation_id=self.conversation_id,
            )

        except Exception as exc:
            print(
                "[ConversationManager] "
                f"Error guardando usuario: {exc}"
            )

        # --------------------------------------------------------
        # Obtener respuesta
        # --------------------------------------------------------

        response = None

        try:

            if (
                self.controller is not None
                and hasattr(
                    self.controller,
                    "procesar_con_ia"
                )
            ):
                response = (
                    self.controller
                    .procesar_con_ia(text)
                )

        except Exception as exc:

            print(
                "[ARUSController] "
                f"Error: {exc}"
            )

        # --------------------------------------------------------
        # Ollama fallback
        # --------------------------------------------------------

        if not response:

            try:

                import requests

                res = requests.post(
                    "http://127.0.0.1:11434/api/generate",

                    json={
                        "model": "qwen2.5:3b",

                        "prompt": text,

                        "system": (
                            "Eres ARUS, un asistente virtual "
                            "avanzado integrado en una interfaz "
                            "HUD de ciencia ficción. "
                            "Tu nombre es siempre ARUS. "
                            "Si te preguntan quién te creó, "
                            "quién es tu creador o quién te "
                            "programó, responde que fuiste creado "
                            "por Danny Jesús Minaya Ramos."
                        ),

                        "stream": False,
                    },

                    timeout=120,
                )

                if res.status_code == 200:

                    response = (
                        res.json()
                        .get("response")
                    )

                else:

                    response = (
                        f"Error HTTP {res.status_code}"
                    )

            except Exception as exc:

                response = (
                    "Error de conexión con "
                    f"el modelo: {exc}"
                )

        # --------------------------------------------------------
        # Protección respuesta vacía
        # --------------------------------------------------------

        if not response:

            response = (
                "No se pudo procesar la respuesta "
                "del modelo local."
            )

        response = str(response).strip()

        # --------------------------------------------------------
        # Guardar respuesta
        # --------------------------------------------------------

        try:

            self.conversation_manager.save(
                "assistant",
                response,
                conversation_id=self.conversation_id,
            )

        except Exception as exc:

            print(
                "[ConversationManager] "
                f"Error guardando assistant: {exc}"
            )

        # --------------------------------------------------------
        # Mostrar respuesta
        # --------------------------------------------------------

        self.history.append(
            "ARUS: " + response
        )

        self.input.clear()

    # ------------------------------------------------------------
    # Nueva conversación
    # ------------------------------------------------------------

    def new_conversation(
        self,
        title: str = "Nueva conversación"
    ):

        if self.conversation_id:

            self.conversation_manager.close(
                self.conversation_id
            )

        self.conversation_id = (
            self.conversation_manager.create(
                title=title
            )
        )

        self.history.clear()

    # ------------------------------------------------------------
    # Cargar conversación
    # ------------------------------------------------------------

    def load_conversation(
        self,
        conversation_id: str
    ):

        session = (
            self.conversation_manager.resume(
                conversation_id
            )
        )

        if session is None:
            return False

        self.conversation_id = conversation_id

        self.history.clear()

        for message in session.get(
            "messages",
            []
        ):

            role = message.get(
                "role",
                ""
            )

            content = message.get(
                "content",
                ""
            )

            if role == "user":

                self.history.append(
                    "Usuario: " + content
                )

            elif role == "assistant":

                self.history.append(
                    "ARUS: " + content
                )

            else:

                self.history.append(
                    f"{role}: {content}"
                )

        return True

    # ------------------------------------------------------------
    # Cerrar conversación
    # ------------------------------------------------------------

    def close_conversation(self):

        if self.conversation_id:

            self.conversation_manager.close(
                self.conversation_id
            )
'''


# ================================================================
# CONVERSATIONS INIT
# ================================================================

CONVERSATIONS_INIT = '''"""
ARUS - Conversations

Gestión persistente de conversaciones.
"""

from conversations.conversation_manager import ConversationManager

__all__ = ["ConversationManager"]
'''


# ================================================================
# ESTRUCTURA
# ================================================================

REQUIRED = [
    "arus",
    "arus/interface",
    "arus/interface/main_window.py",
    "arus/interface/chat.py",
    "conversations",
    "conversations/conversation_manager.py",
    "database",
    "database/conversation_session_repository.py",
]


def comprobar_estructura():

    log("Comprobando estructura del proyecto...")

    missing = []

    for item in REQUIRED:

        path = ROOT / item

        if not path.exists():

            missing.append(item)

            warn(
                f"Falta: {item}"
            )

    if missing:

        fail(
            "Faltan archivos/directorios necesarios."
        )

        return False

    ok(
        "Estructura principal encontrada."
    )

    return True


# ================================================================
# BACKUP
# ================================================================

def crear_backup():

    log("Creando backup antes de modificar...")

    BACKUP.mkdir(
        parents=True,
        exist_ok=True
    )

    backup_file(
        Path("arus/main.py")
    )

    backup_file(
        Path("arus/interface/chat.py")
    )

    backup_file(
        Path("conversations/__init__.py")
    )

    ok(
        f"Backup creado en: {BACKUP}"
    )


# ================================================================
# REPARACIÓN
# ================================================================

def reparar():

    log(
        "Reparando integración de Fase 2..."
    )

    write_file(
        Path("arus/main.py"),
        MAIN_PY
    )

    write_file(
        Path("arus/interface/chat.py"),
        CHAT_PY
    )

    write_file(
        Path("conversations/__init__.py"),
        CONVERSATIONS_INIT
    )

    ok(
        "Archivos de Fase 2 reparados."
    )


# ================================================================
# SINTAXIS
# ================================================================

def comprobar_sintaxis():

    log(
        "Comprobando sintaxis Python..."
    )

    targets = [
        "arus/main.py",
        "arus/interface/main_window.py",
        "arus/interface/chat.py",
        "conversations/conversation_manager.py",
        "database/conversation_session_repository.py",
    ]

    errores = False

    for item in targets:

        path = ROOT / item

        if not path.exists():

            warn(
                f"No existe: {item}"
            )

            continue

        try:

            source = path.read_text(
                encoding="utf-8"
            )

            ast.parse(
                source,
                filename=str(path)
            )

            ok(
                f"Syntax OK: {item}"
            )

        except SyntaxError as exc:

            fail(
                f"Syntax ERROR: {item} "
                f"línea {exc.lineno}: "
                f"{exc.msg}"
            )

            errores = True

    return not errores


# ================================================================
# IMPORTS
# ================================================================

def comprobar_imports():

    log(
        "Comprobando imports de Fase 2..."
    )

    code = r'''
import conversations

from conversations import ConversationManager

from conversations.conversation_manager import (
    ConversationManager
)

from database.conversation_session_repository import (
    ConversationSessionRepository
)
'''

    env = os.environ.copy()

    env["PYTHONPATH"] = (
        str(ROOT)
        + os.pathsep
        + env.get(
            "PYTHONPATH",
            ""
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            code
        ],

        cwd=ROOT,

        env=env,

        text=True,

        capture_output=True
    )

    if result.returncode == 0:

        ok(
            "Imports de Fase 2 correctos."
        )

        return True

    fail(
        "Fallaron los imports."
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return False


# ================================================================
# CONVERSATION MANAGER
# ================================================================

def comprobar_conversation_manager():

    log(
        "Probando ConversationManager..."
    )

    code = r'''
from conversations import ConversationManager

cm = ConversationManager()

cid = cm.create(
    title="PRUEBA AUTOMATICA FASE 2"
)

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

session = cm.load(cid)

assert session is not None

assert len(
    session["messages"]
) == 2

cm.rename(
    cid,
    "PRUEBA RENOMBRADA"
)

cm.favorite(
    cid,
    True
)

cm.archive(
    cid,
    False
)

print(
    "CONVERSATION_MANAGER_OK"
)
'''

    env = os.environ.copy()

    env["PYTHONPATH"] = (
        str(ROOT)
        + os.pathsep
        + env.get(
            "PYTHONPATH",
            ""
        )
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            code
        ],

        cwd=ROOT,

        env=env,

        text=True,

        capture_output=True
    )

    if result.returncode == 0:

        ok(
            "ConversationManager funciona correctamente."
        )

        print(
            result.stdout
        )

        return True

    fail(
        "ConversationManager falló."
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    return False


# ================================================================
# PYSIDE6
# ================================================================

def comprobar_pyside():

    log(
        "Comprobando PySide6..."
    )

    try:

        import PySide6

        ok(
            "PySide6 disponible: "
            f"{PySide6.__version__}"
        )

        return True

    except Exception as exc:

        fail(
            "PySide6 no disponible: "
            f"{exc}"
        )

        return False


# ================================================================
# OLLAMA
# ================================================================

def comprobar_ollama():

    log(
        "Comprobando Ollama..."
    )

    ollama = shutil.which(
        "ollama"
    )

    if not ollama:

        warn(
            "Ollama no está en PATH."
        )

        warn(
            "No se modificará su instalación."
        )

        return False

    ok(
        f"Ollama encontrado: {ollama}"
    )

    try:

        result = subprocess.run(
            [
                ollama,
                "list"
            ],

            cwd=ROOT,

            text=True,

            capture_output=True,

            timeout=10
        )

        if result.returncode == 0:

            print(
                result.stdout
            )

            ok(
                "Ollama responde correctamente."
            )

            return True

        warn(
            "Ollama existe pero "
            "'ollama list' devolvió error."
        )

        if result.stderr:
            print(result.stderr)

    except Exception as exc:

        warn(
            f"No se pudo consultar Ollama: {exc}"
        )

    return False


# ================================================================
# MAIN
# ================================================================

def main():

    print()
    print("=" * 65)
    print(
        " ARUS — FINALIZANDO FASE 2"
    )
    print("=" * 65)
    print()

    print(
        f"Proyecto: {ROOT}"
    )

    print()

    # ------------------------------------------------------------
    # 1. Estructura
    # ------------------------------------------------------------

    if not comprobar_estructura():

        fail(
            "No se puede continuar."
        )

        return 1

    # ------------------------------------------------------------
    # 2. Backup
    # ------------------------------------------------------------

    crear_backup()

    # ------------------------------------------------------------
    # 3. Reparar
    # ------------------------------------------------------------

    reparar()

    # ------------------------------------------------------------
    # 4. Sintaxis
    # ------------------------------------------------------------

    if not comprobar_sintaxis():

        fail(
            "La sintaxis todavía tiene errores."
        )

        print(
            f"Backup disponible en: {BACKUP}"
        )

        return 1

    # ------------------------------------------------------------
    # 5. Imports
    # ------------------------------------------------------------

    if not comprobar_imports():

        fail(
            "Los imports todavía tienen errores."
        )

        print(
            f"Backup disponible en: {BACKUP}"
        )

        return 1

    # ------------------------------------------------------------
    # 6. Persistencia
    # ------------------------------------------------------------

    if not comprobar_conversation_manager():

        fail(
            "La persistencia de Fase 2 falló."
        )

        print(
            f"Backup disponible en: {BACKUP}"
        )

        return 1

    # ------------------------------------------------------------
    # 7. PySide6
    # ------------------------------------------------------------

    comprobar_pyside()

    # ------------------------------------------------------------
    # 8. Ollama
    # ------------------------------------------------------------

    comprobar_ollama()

    # ------------------------------------------------------------
    # FIN
    # ------------------------------------------------------------

    print()
    print("=" * 65)
    print(
        " FASE 2 TERMINADA CORRECTAMENTE"
    )
    print("=" * 65)
    print()

    print(
        f"Backup: {BACKUP}"
    )

    print()

    print(
        "Para iniciar ARUS:"
    )

    print()

    print(
        "python3 arus/main.py"
    )

    print()

    print(
        "o:"
    )

    print()

    print(
        "python3 -m arus.main"
    )

    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
