"""
ARUS MARK 7 - Fase 3
Test real de ContextManager (no pseudocodigo).

Ejecutar desde la raiz del proyecto:
    python context_tests/test_fase3_context_manager.py

Requiere que la Fase 2 (conversations/ConversationManager) ya este instalada.
No modifica arus/interface/, brain.py ni memory_manager.py.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, ".")

import arus.core.paths as paths
paths.DATA_DIR = Path(tempfile.mkdtemp())  # DB temporal, no toca tu arus.db real

from conversations.conversation_manager import ConversationManager
from context.context_manager import ContextManager


def run():
    print("--- Test 1: API retrocompatible (sin conversation_manager) ---")
    cm_old = ContextManager(max_messages=5)
    cm_old.add_user_message("hola")
    cm_old.add_assistant_message("hola, en que ayudo?")
    assert cm_old.get_context() == [
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "hola, en que ayudo?"},
    ]
    cm_old.clear()
    assert cm_old.get_context() == []
    print("OK")

    print("--- Test 2: contexto vacio ---")
    cm2 = ContextManager(conversation_manager=ConversationManager())
    assert cm2.get_context("no-existe") == []
    print("OK")

    print("--- Test 3: crear, anadir mensajes, orden correcto, persistencia real ---")
    conv = ConversationManager()
    ctx = ContextManager(conversation_manager=conv, max_messages=20)
    cid = conv.create(title="Fase 3 test")
    ctx.add_message("user", "Hola ARUS.", conversation_id=cid)
    ctx.add_message("assistant", "Hola Danny.", conversation_id=cid)
    ctx.add_message("user", "Mi proyecto se llama ARUS MARK 7.", conversation_id=cid)
    c = ctx.get_context(cid)
    assert [m["content"] for m in c] == [
        "Hola ARUS.", "Hola Danny.", "Mi proyecto se llama ARUS MARK 7.",
    ]
    persisted = conv.load(cid)
    assert len(persisted["messages"]) == 3
    print("OK")

    print("--- Test 4: conversaciones independientes (no se mezclan) ---")
    cid_b = conv.create(title="Otra conversacion")
    ctx.add_message("user", "Este es otro tema.", conversation_id=cid_b)
    assert ctx.get_context(cid)[0]["content"] == "Hola ARUS."
    assert ctx.get_context(cid_b)[0]["content"] == "Este es otro tema."
    print("OK")

    print("--- Test 5: resume() reconstruye contexto desde Fase 2 ---")
    ctx_fresh = ContextManager(conversation_manager=conv)
    rebuilt = ctx_fresh.resume(cid)
    assert [m["content"] for m in rebuilt] == [
        "Hola ARUS.", "Hola Danny.", "Mi proyecto se llama ARUS MARK 7.",
    ]
    print("OK")

    print("--- Test 6: limites de contexto / compactacion en conversacion larga ---")
    ctx_small = ContextManager(conversation_manager=conv, max_messages=6)
    cid_c = conv.create(title="Conversacion larga")
    for i in range(15):
        ctx_small.add_message("user", f"mensaje numero {i}", conversation_id=cid_c)
    final_ctx = ctx_small.get_context(cid_c)
    assert len(final_ctx) <= 6
    session = conv.load(cid_c)
    assert session["summary"] is not None
    assert len(session["messages"]) == 15
    print("OK - contexto recortado a", len(final_ctx), "| persistencia integra:", len(session["messages"]))

    print("--- Test 7: manejo de errores (resume sin conversation_manager) ---")
    ctx_no_cm = ContextManager()
    try:
        ctx_no_cm.resume("algun-id")
        raise SystemExit("debia lanzar error")
    except RuntimeError as e:
        print("OK -", e)

    print("--- Test 8: resume de conversacion inexistente ---")
    assert ctx_fresh.resume("id-que-no-existe") == []
    print("OK")

    print("--- Test 9: to_prompt usa ContextBuilder existente ---")
    texto = ctx.to_prompt(cid)
    assert "user: Hola ARUS." in texto
    print("OK")

    print()
    print("TODOS LOS TESTS DE FASE 3 PASARON")


if __name__ == "__main__":
    run()
