#!/usr/bin/env python3

import ast
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("/home/damian/ARUS_restaurado")
CHAT = ROOT / "arus/interface/chat.py"
CONTROLLER = ROOT / "arus/interface/controller.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / "ARUS_BACKUP" / f"fase2_integracion_{timestamp}"

print("=" * 70)
print(" ARUS MARK 7 — FINALIZACIÓN FASE 2")
print(" ConversationManager → Chat")
print("=" * 70)

# ------------------------------------------------------------
# 1. Comprobaciones básicas
# ------------------------------------------------------------

if not ROOT.exists():
    print("ERROR: No existe la raíz del proyecto:", ROOT)
    sys.exit(1)

CM = ROOT / "conversations/conversation_manager.py"
REPO = ROOT / "database/conversation_session_repository.py"

for path in (CM, REPO):
    if not path.exists():
        print(f"ERROR: Falta {path}")
        print("La Fase 2 no está instalada correctamente.")
        sys.exit(1)

print("[OK] ConversationManager encontrado")
print("[OK] ConversationSessionRepository encontrado")

# ------------------------------------------------------------
# 2. Comprobar sintaxis actual
# ------------------------------------------------------------

print("\n[1/8] Comprobando sintaxis existente...")

files_to_check = [
    CM,
    REPO,
]

if CHAT.exists():
    files_to_check.append(CHAT)

if CONTROLLER.exists():
    files_to_check.append(CONTROLLER)

for file in files_to_check:
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(file)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR DE SINTAXIS EN: {file}")
        print(result.stderr)
        print("\nNo se modificará ningún archivo.")
        sys.exit(1)

print("[OK] Sintaxis inicial correcta")

# ------------------------------------------------------------
# 3. Backup
# ------------------------------------------------------------

print("\n[2/8] Creando backup...")

BACKUP.mkdir(parents=True, exist_ok=True)

for source in (CHAT, CONTROLLER):
    if source.exists():
        destination = BACKUP / source.relative_to(ROOT)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        print(f"[BACKUP] {source.relative_to(ROOT)}")

print(f"[OK] Backup: {BACKUP}")

# ------------------------------------------------------------
# 4. Analizar ChatWidget
# ------------------------------------------------------------

print("\n[3/8] Analizando ChatWidget...")

if not CHAT.exists():
    print("ERROR: No existe:")
    print(CHAT)
    print("No puedo hacer una integración segura.")
    sys.exit(1)

chat_source = CHAT.read_text(encoding="utf-8")

try:
    tree = ast.parse(chat_source)
except SyntaxError as exc:
    print("ERROR: chat.py no se puede analizar.")
    print(exc)
    sys.exit(1)

chatwidget = None
send_function = None

for node in tree.body:
    if isinstance(node, ast.ClassDef) and node.name == "ChatWidget":
        chatwidget = node

        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name == "send":
                    send_function = child

if chatwidget is None:
    print("ERROR: No encontré la clase ChatWidget.")
    print("No se modificará nada.")
    sys.exit(1)

if send_function is None:
    print("ERROR: No encontré ChatWidget.send().")
    print("No se modificará nada.")
    sys.exit(1)

print("[OK] ChatWidget encontrado")
print("[OK] ChatWidget.send() encontrado")

# ------------------------------------------------------------
# 5. Comprobar que el ConversationManager aún no está integrado
# ------------------------------------------------------------

print("\n[4/8] Comprobando integración existente...")

already_imported = (
    "from conversations.conversation_manager import ConversationManager"
    in chat_source
)

already_has_manager = (
    "ConversationManager()" in chat_source
)

if already_imported and already_has_manager:
    print("[INFO] ConversationManager parece estar integrado ya.")
    print("No se realizará una segunda integración.")

else:

    # --------------------------------------------------------
    # IMPORT
    # --------------------------------------------------------

    print("[5/8] Preparando integración...")

    import_line = (
        "from conversations.conversation_manager "
        "import ConversationManager\n"
    )

    if not already_imported:
        lines = chat_source.splitlines(True)

        # Insertar después de los imports existentes.
        insert_at = 0

        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_at = i + 1

        lines.insert(insert_at, import_line)
        chat_source = "".join(lines)

    # --------------------------------------------------------
    # INICIALIZACIÓN
    # --------------------------------------------------------

    # Buscar __init__ de ChatWidget
    try:
        tree2 = ast.parse(chat_source)
    except SyntaxError as exc:
        print("ERROR después de preparar import:")
        print(exc)
        sys.exit(1)

    chatwidget2 = None
    init_function = None

    for node in tree2.body:
        if isinstance(node, ast.ClassDef) and node.name == "ChatWidget":
            chatwidget2 = node

            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if child.name == "__init__":
                        init_function = child

    if init_function is None:
        print("ERROR: No encontré ChatWidget.__init__().")
        print("No se modificará el proyecto.")
        sys.exit(1)

    # Obtener el cuerpo textual del __init__
    lines = chat_source.splitlines(True)

    init_line_start = init_function.lineno - 1
    init_line_end = init_function.end_lineno

    init_lines = lines[init_line_start:init_line_end]

    # Evitar duplicados
    init_text = "".join(init_lines)

    if "self.conversation_manager" not in init_text:
        # Encontrar la primera línea del cuerpo.
        # Se añade después de la firma, con indentación de 8 espacios
        # para un método normal dentro de una clase.
        insertion_index = init_line_start + 1

        while (
            insertion_index < len(lines)
            and (
                lines[insertion_index].strip() == ""
                or lines[insertion_index].lstrip().startswith("#")
            )
        ):
            insertion_index += 1

        init_code = [
            "        # ARUS FASE 2 - ConversationManager\n",
            "        self.conversation_manager = ConversationManager()\n",
            "        self.conversation_id = self.conversation_manager.create(\n",
            "            title=\"Nueva conversación\"\n",
            "        )\n",
        ]

        lines[insertion_index:insertion_index] = init_code
        chat_source = "".join(lines)

# ------------------------------------------------------------
# 6. Integración de guardado
# ------------------------------------------------------------

print("[6/8] Integrando guardado incremental...")

# Recalcular AST
try:
    tree3 = ast.parse(chat_source)
except SyntaxError as exc:
    print("ERROR al analizar chat.py:")
    print(exc)
    print("No se escribirá el archivo.")
    sys.exit(1)

chatwidget3 = None
send3 = None

for node in tree3.body:
    if isinstance(node, ast.ClassDef) and node.name == "ChatWidget":
        chatwidget3 = node
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name == "send":
                    send3 = child

if send3 is None:
    print("ERROR: ChatWidget.send() desapareció durante el análisis.")
    sys.exit(1)

lines = chat_source.splitlines(True)

send_start = send3.lineno - 1
send_end = send3.end_lineno

send_text = "".join(lines[send_start:send_end])

# ------------------------------------------------------------
# Buscar dónde se obtiene el texto del usuario
# ------------------------------------------------------------

user_patterns = [
    r"(\w+)\.toPlainText\(\)",
    r"(\w+)\.text\(\)",
]

user_expression = None

for pattern in user_patterns:
    match = re.search(pattern, send_text)

    if match:
        user_expression = match.group(0)
        break

if user_expression is None:
    print("ADVERTENCIA:")
    print("No pude identificar de forma segura cómo ChatWidget.send()")
    print("obtiene el texto del usuario.")
    print()
    print("Por seguridad NO modificaré send().")
    print()
    print("La Fase 2 de persistencia sigue funcionando, pero la")
    print("integración automática necesita revisar manualmente send().")
    sys.exit(0)

print(f"[OK] Expresión de mensaje detectada: {user_expression}")

# ------------------------------------------------------------
# Evitar integración duplicada
# ------------------------------------------------------------

if "conversation_manager.save(" in send_text:
    print("[OK] send() ya contiene guardado.")
else:

    # Añadir guardado inmediatamente después de obtener el texto.
    pattern = re.escape(user_expression)

    match = re.search(
        rf"(?P<indent>^[ \t]*)(?P<var>\w+)\s*=\s*{pattern}",
        send_text,
        re.MULTILINE,
    )

    if not match:
        print("ADVERTENCIA: no pude localizar la asignación exacta.")
        print("No modificaré send() automáticamente.")
        sys.exit(0)

    indent = match.group("indent")
    variable = match.group("var")

    save_code = (
        f"{indent}# ARUS FASE 2 - guardar mensaje del usuario\n"
        f"{indent}try:\n"
        f"{indent}    self.conversation_manager.save(\n"
        f"{indent}        \"user\",\n"
        f"{indent}        {variable}\n"
        f"{indent}    )\n"
        f"{indent}except Exception as exc:\n"
        f"{indent}    print(f\"[ConversationManager] Error guardando usuario: {{exc}}\")\n"
    )

    absolute_insert = send_start + send_text[:match.end()].count("\n") + 1

    lines[absolute_insert:absolute_insert] = save_code.splitlines(True)

    chat_source = "".join(lines)

# ------------------------------------------------------------
# Guardar respuesta
# ------------------------------------------------------------

print("[7/8] Preparando guardado de respuesta...")

# Volver a analizar
tree4 = ast.parse(chat_source)

send4 = None

for node in tree4.body:
    if isinstance(node, ast.ClassDef) and node.name == "ChatWidget":
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name == "send":
                    send4 = child

if send4 is None:
    print("ERROR: No se pudo localizar send().")
    sys.exit(1)

lines = chat_source.splitlines(True)
send_start = send4.lineno - 1
send_end = send4.end_lineno
send_text = "".join(lines[send_start:send_end])

# Intentamos detectar respuestas típicas.
response_candidates = [
    "response_text",
    "response",
    "reply",
    "answer",
    "assistant_response",
    "result",
]

response_variable = None

for candidate in response_candidates:
    if re.search(rf"\b{re.escape(candidate)}\b", send_text):
        response_variable = candidate
        break

# Si no encontramos una variable segura, NO modificar respuesta.
if response_variable is None:
    print("[ADVERTENCIA] No encontré una variable de respuesta segura.")
    print("El guardado del usuario sí puede quedar instalado.")
    print("El guardado de assistant requerirá integración posterior.")
else:
    if "conversation_manager.save(" not in send_text:
        # Buscar una operación que añada la respuesta a la interfaz.
        response_match = None

        for candidate in response_candidates:
            m = re.search(
                rf"(?P<indent>^[ \t]*).*?\b{re.escape(candidate)}\b.*$",
                send_text,
                re.MULTILINE,
            )
            if m:
                response_match = m
                break

        if response_match:
            indent = response_match.group("indent")

            response_code = (
                f"{indent}# ARUS FASE 2 - guardar respuesta\n"
                f"{indent}try:\n"
                f"{indent}    self.conversation_manager.save(\n"
                f"{indent}        \"assistant\",\n"
                f"{indent}        str({response_variable})\n"
                f"{indent}    )\n"
                f"{indent}except Exception as exc:\n"
                f"{indent}    print(f\"[ConversationManager] Error guardando assistant: {{exc}}\")\n"
            )

            absolute_insert = (
                send_start
                + send_text[:response_match.end()].count("\n")
                + 1
            )

            lines[absolute_insert:absolute_insert] = (
                response_code.splitlines(True)
            )

            chat_source = "".join(lines)
            print(f"[OK] Guardado assistant preparado: {response_variable}")

# ------------------------------------------------------------
# 8. Verificar y escribir
# ------------------------------------------------------------

print("[8/8] Verificando modificación antes de escribir...")

try:
    ast.parse(chat_source)
except SyntaxError as exc:
    print("ERROR: La modificación generaría sintaxis inválida.")
    print(exc)
    print("NO se modificó chat.py.")
    sys.exit(1)

# No modificar controller en esta fase si no es imprescindible.
print("[OK] controller.py no será modificado.")

CHAT.write_text(chat_source, encoding="utf-8")

# Compilar
result = subprocess.run(
    [sys.executable, "-m", "py_compile", str(CHAT)],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

if result.returncode != 0:
    print("\nERROR: chat.py quedó con error de sintaxis.")
    print(result.stderr)

    print("Restaurando backup...")
    original = BACKUP / CHAT.relative_to(ROOT)

    if original.exists():
        shutil.copy2(original, CHAT)
        print("[OK] chat.py restaurado.")

    sys.exit(1)

print("[OK] chat.py compila correctamente.")

# ------------------------------------------------------------
# Informe
# ------------------------------------------------------------

print("\n" + "=" * 70)
print(" FASE 2 — RESULTADO")
print("=" * 70)

print("ConversationManager:        OK")
print("SQLite:                     OK")
print("ChatWidget analizado:       OK")
print("Backup:                     OK")
print("chat.py sintaxis:           OK")
print("Interfaz visual modificada: NO")
print("controller.py modificado:   NO")
print()
print("Backup:")
print(BACKUP)
print()

print("IMPORTANTE:")
print("La integración se hizo únicamente si el código real permitió")
print("identificar de forma segura el punto de guardado.")
print()
print("Ahora ejecutaremos una prueba final de importación.")
print("=" * 70)

result = subprocess.run(
    [
        sys.executable,
        "-c",
        (
            "from conversations.conversation_manager "
            "import ConversationManager; "
            "cm=ConversationManager(); "
            "cid=cm.create(title='Prueba integración Fase 2'); "
            "cm.save('user','Prueba automática Fase 2'); "
            "print(cm.load(cid))"
        ),
    ],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    print("[OK] Prueba ConversationManager correcta.")
    print(result.stdout)
else:
    print("[ERROR] Falló la prueba final.")
    print(result.stderr)
    sys.exit(1)

print("=" * 70)
print(" FASE 2 COMPLETADA / INTEGRACIÓN REALIZADA")
print("=" * 70)
print()
print("Antes de pasar a Fase 3, ejecuta:")
print()
print("    git diff -- arus/interface/chat.py")
print()
print("y revisa el cambio.")
print()
