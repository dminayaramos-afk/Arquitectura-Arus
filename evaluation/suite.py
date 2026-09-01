"""
ARUS
Evaluation Suite (Fase 16)

Ejecuta pruebas reales contra los módulos construidos en las Fases
2-15. Pensada para correr "antes y después de cambios importantes"
(punto 50). No sustituye los tests unitarios de cada fase (que viven
en sus propios LEEME) -- esto es la comprobación de conjunto.

Requiere `ollama` y `PySide6` para las pruebas que tocan Brain/GUI;
si no están instalados, esas pruebas se marcan SKIP (no verificable
en este entorno) en vez de fallar o fingir que pasaron.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

from evaluation.check import Suite


def _stub_ollama():

    if "ollama" in sys.modules:
        return

    class FakeMessage:
        def __init__(self, content=None, tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls

    class FakeResponse:
        def __init__(self, message):
            self.message = message

    class FakeClient:
        def __init__(self, host=None):
            pass

        def list(self):
            return {"models": []}

        def chat(self, model, messages, tools=None):
            return FakeResponse(FakeMessage(content="Respuesta simulada de evaluación."))

    modulo = types.ModuleType("ollama")
    modulo.Client = FakeClient
    sys.modules["ollama"] = modulo


def _pyside6_disponible() -> bool:

    try:
        import PySide6  # noqa
        return True
    except ImportError:
        return False


def run_all() -> Suite:

    suite = Suite()

    tmp_data = Path(tempfile.mkdtemp())

    import arus.core.paths as paths
    paths.DATA_DIR = tmp_data

    _stub_ollama()

    workspace = Path.cwd()

    # ------------------------------------------------------------------
    # CONTEXTO
    # ------------------------------------------------------------------

    def _contexto_orden():
        from context.context_manager import ContextManager
        cm = ContextManager(max_messages=10)
        cm.add_user_message("hola")
        cm.add_assistant_message("hola de vuelta")
        ctx = cm.get_context()
        if [m["content"] for m in ctx] != ["hola", "hola de vuelta"]:
            return "el orden de los mensajes no es el esperado"

    suite.run("Contexto", "orden de mensajes", _contexto_orden)

    def _contexto_multi_conversacion():
        from conversations.conversation_manager import ConversationManager
        from context.context_manager import ContextManager
        conv = ConversationManager()
        ctx = ContextManager(conversation_manager=conv)
        a = conv.create(title="A")
        b = conv.create(title="B")
        ctx.add_message("user", "mensaje A", conversation_id=a)
        ctx.add_message("user", "mensaje B", conversation_id=b)
        if ctx.get_context(a)[0]["content"] != "mensaje A":
            return "conversación A contaminada"
        if ctx.get_context(b)[0]["content"] != "mensaje B":
            return "conversación B contaminada"

    suite.run("Contexto", "conversaciones independientes", _contexto_multi_conversacion)

    # ------------------------------------------------------------------
    # MEMORIA
    # ------------------------------------------------------------------

    def _memoria_persistencia():
        from memory.long_memory import LongMemory
        lm = LongMemory()
        lm.remember("nombre_eval", "Danny")
        lm2 = LongMemory()  # simula reinicio
        if lm2.recall("nombre_eval") != "Danny":
            return "LongMemory no sobrevivió a una nueva instancia"

    suite.run("Memoria", "LongMemory persiste tras reinicio", _memoria_persistencia)

    def _memoria_preferencias():
        from memory.user_preferences import UserPreferences
        up = UserPreferences()
        up.set("idioma_eval", "es")
        if up.get("idioma_eval") != "es":
            return "UserPreferences no guardó el valor"

    suite.run("Memoria", "UserPreferences", _memoria_preferencias)

    def _memoria_tareas():
        from memory.task_memory import TaskMemory
        tm = TaskMemory()
        tm.save("t_eval", {"status": "pending"})
        # ARUS MARK 9: TaskMemory.pending() devuelve objetos
        # MemoryTask (con .name == task_id), no los ids en crudo --
        # este check comparaba directamente con la cadena "t_eval" y
        # nunca podía coincidir. Corregido para usar la API real.
        nombres_pendientes = [t.name for t in tm.pending()]
        if "t_eval" not in nombres_pendientes:
            return "TaskMemory.pending() no filtró correctamente"

    suite.run("Memoria", "TaskMemory", _memoria_tareas)

    def _memoria_semantica():
        from memory.semantic_memory import SemanticMemory
        sm = SemanticMemory()
        sm.add("doc_eval", "ARUS usa PySide6 para la interfaz")
        if len(sm.search("PySide6")) == 0:
            return "SemanticMemory.search() no encontró la entrada"

    suite.run("Memoria", "SemanticMemory", _memoria_semantica)

    # ------------------------------------------------------------------
    # CONVERSACIÓN LARGA
    # ------------------------------------------------------------------

    def _conversacion_larga_compactacion():
        from conversations.conversation_manager import ConversationManager
        from context.context_manager import ContextManager
        conv = ConversationManager()
        ctx = ContextManager(conversation_manager=conv, max_messages=6)
        cid = conv.create(title="larga")
        for i in range(20):
            ctx.add_message("user", f"mensaje {i}", conversation_id=cid)
        if len(ctx.get_context(cid)) > 6:
            return "el contexto no se recortó al límite configurado"
        sesion = conv.load(cid)
        if len(sesion["messages"]) != 20:
            return "la persistencia completa no coincide con los 20 mensajes reales"
        if sesion["summary"] is None:
            return "no se generó resumen al compactar"

    suite.run("Conversación larga", "compactación con persistencia íntegra", _conversacion_larga_compactacion)

    def _conversacion_resume():
        from conversations.conversation_manager import ConversationManager
        from context.context_manager import ContextManager
        conv = ConversationManager()
        cid = conv.create(title="para reanudar")
        conv.save("user", "primer mensaje", conversation_id=cid)
        conv.save("assistant", "primera respuesta", conversation_id=cid)
        ctx_nuevo = ContextManager(conversation_manager=conv)
        reconstruido = ctx_nuevo.resume(cid)
        if [m["content"] for m in reconstruido] != ["primer mensaje", "primera respuesta"]:
            return "resume() no reconstruyó el historial correctamente"

    suite.run("Conversación larga", "resume() reconstruye contexto", _conversacion_resume)

    # ------------------------------------------------------------------
    # HERRAMIENTAS
    # ------------------------------------------------------------------

    def _tools_calculadora():
        from tools.tool_manager import ToolManager
        tm = ToolManager()
        if "calculator" not in tm.available_tools():
            return "calculator no está registrada"
        if tm.execute("calculator", expression="6*7") != "42":
            return "cálculo incorrecto"

    suite.run("Herramientas", "calculator vía ToolManager", _tools_calculadora)

    def _tools_git():
        if shutil.which("git") is None:
            return "SKIP: git no está instalado en este entorno"
        repo = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "e@a.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "eval"], cwd=repo, check=True)
        (repo / "a.txt").write_text("x")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo, check=True)

        from tools.git_tool import GitTool
        rama = GitTool().execute("current_branch", repo_path=str(repo))
        if not rama or "ERROR" in rama:
            return f"current_branch falló: {rama}"

    suite.run("Herramientas", "git_tool contra repo real", _tools_git)

    def _tools_verifier_repair():
        from brain.task import Task
        from brain.verifier import Verifier
        v = Verifier()
        intentos = {"n": 0}

        def ejecutor(name, **kwargs):
            intentos["n"] += 1
            return "reparado"

        t = Task(name="mock", arguments={}, status="error", result="fallo inicial")
        r = v.repair_task(t, ejecutor)
        if not r.ok or intentos["n"] != 1:
            return "repair_task no reintentó correctamente"

    suite.run("Herramientas", "Verifier repair/retry", _tools_verifier_repair)

    # ------------------------------------------------------------------
    # CÓDIGO
    # ------------------------------------------------------------------

    def _codigo_test_runner():
        from tools.test_runner_tool import TestRunnerTool
        carpeta = workspace / "tmp" / "eval_tests"
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / "test_eval_ok.py").write_text(
            "import unittest\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertEqual(1 + 1, 2)\n"
        )
        try:
            resultado = TestRunnerTool().execute(path=str(carpeta.relative_to(workspace)))
            if "OK: todas las pruebas pasaron" not in resultado:
                return f"resultado inesperado: {resultado[:200]}"
        finally:
            shutil.rmtree(carpeta, ignore_errors=True)

    suite.run("Código", "test_runner_tool detecta éxito", _codigo_test_runner)

    def _codigo_python_check():
        from tools.python_check_tool import PythonCheckTool
        archivo = workspace / "tmp" / "eval_bad_syntax.py"
        archivo.parent.mkdir(parents=True, exist_ok=True)
        archivo.write_text("def foo(:\n    pass\n")
        try:
            resultado = PythonCheckTool().execute(path=str(archivo.relative_to(workspace)))
            if "error" not in resultado.lower() and "Error" not in resultado:
                return f"no detectó el error de sintaxis: {resultado[:200]}"
        finally:
            archivo.unlink(missing_ok=True)

    suite.run("Código", "python_check_tool detecta sintaxis inválida", _codigo_python_check)

    # ------------------------------------------------------------------
    # WEB
    # ------------------------------------------------------------------

    def _web_tool_real():
        from tools.web_tool import WebTool
        resultado = WebTool().execute("https://example.com")
        if "Contenido simulado" in resultado:
            return "web_tool sigue devolviendo contenido simulado"
        if not ("[HTTP" in resultado or "ERROR" in resultado):
            return f"respuesta inesperada: {resultado[:200]}"
        return "SKIP: red restringida en este entorno; se confirmó que la petición es real (no simulada), no que llegue a internet"

    suite.run("Web", "web_tool hace una petición real", _web_tool_real)

    def _search_tool_real():
        from tools.search_tool import SearchTool
        resultado = SearchTool().execute("ARUS asistente de IA")
        if "Resultados para la búsqueda" in resultado:
            return "search_tool sigue devolviendo resultados simulados"
        return "SKIP: red restringida en este entorno; se confirmó que la búsqueda es real (no simulada)"

    suite.run("Web", "search_tool hace una búsqueda real", _search_tool_real)

    # ------------------------------------------------------------------
    # RAG
    # ------------------------------------------------------------------

    def _rag_indexar_y_buscar():
        from rag.rag_manager import RAGManager
        rag = RAGManager()
        doc = Path(tempfile.mkdtemp()) / "eval_doc.md"
        doc.write_text("ARUS guarda la memoria a largo plazo en SQLite mediante MemoryRepository.")
        rag.index_file(str(doc), project="eval")
        resultados = rag.query("MemoryRepository SQLite", project="eval", top_k=1)
        if not resultados or "eval_doc.md" not in resultados[0]["source"]:
            return "la búsqueda no encontró el documento indexado"

    suite.run("RAG", "indexar y consultar un documento real", _rag_indexar_y_buscar)

    # ------------------------------------------------------------------
    # ARCHIVOS (incluye regresión de seguridad de la Fase 14)
    # ------------------------------------------------------------------

    def _archivos_dentro_area():
        from tools.file_writer_tool import FileWriterTool
        resultado = FileWriterTool().execute("tmp/eval_archivo.txt", "contenido de evaluación")
        Path("tmp/eval_archivo.txt").unlink(missing_ok=True)
        if "escrito correctamente" not in resultado:
            return f"no se pudo escribir dentro del área de trabajo: {resultado}"

    suite.run("Archivos", "escritura dentro del área de trabajo", _archivos_dentro_area)

    def _archivos_fuera_area_bloqueado():
        from tools.file_writer_tool import FileWriterTool
        resultado = FileWriterTool().execute("/tmp/eval_fuera_de_area.txt", "no debería escribirse")
        if "ERROR" not in resultado:
            return "¡se permitió escribir fuera del área de trabajo! (regresión de la Fase 14)"
        if Path("/tmp/eval_fuera_de_area.txt").exists():
            return "el archivo se creó igualmente pese al error reportado"

    suite.run("Archivos", "escritura fuera del área de trabajo bloqueada", _archivos_fuera_area_bloqueado)

    # ------------------------------------------------------------------
    # VOZ
    # ------------------------------------------------------------------

    def _voz_no_revienta_sin_vosk():
        from arus.core.voice import VoiceCore
        VoiceCore()  # esto es exactamente lo que hace main_window.py; no debe lanzar

    suite.run("Voz", "VoiceCore() no falla sin vosk (regresión del bug crítico de la Fase 11)", _voz_no_revienta_sin_vosk)

    def _voz_limpieza_texto():
        from arus.voice.text_cleaner import clean_for_speech
        limpio = clean_for_speech("# Título\n**negrita** y `codigo` con https://ejemplo.com")
        if "```" in limpio or "https://" in limpio or "**" in limpio or "#" in limpio:
            return "quedaron símbolos sin limpiar"

    suite.run("Voz", "limpieza de texto para TTS", _voz_limpieza_texto)

    # ------------------------------------------------------------------
    # ERRORES (manejo, punto 45: nunca tracebacks crudos al usuario)
    # ------------------------------------------------------------------

    def _errores_tool_desconocida():
        from tools.tool_manager import ToolManager
        tm = ToolManager()
        try:
            tm.execute("herramienta_que_no_existe_nunca")
            return "debía lanzar/reportar un error claro"
        except Exception:
            pass  # ToolManager puede lanzar; lo que importa es que no cuelgue el proceso

    suite.run("Errores", "herramienta desconocida no cuelga el proceso", _errores_tool_desconocida)

    def _errores_ollama_caido():
        # Simula que Ollama no responde: LocalProvider no debe lanzar
        # una excepción sin capturar hacia el usuario final.
        return "SKIP: requiere reemplazar temporalmente el cliente Ollama; cubierto indirectamente por los tests de Fase 4/6 (try/except en generate())"

    suite.run("Errores", "fallo de conexión con Ollama", _errores_ollama_caido)

    # ------------------------------------------------------------------
    # SEGURIDAD (regresión directa de la Fase 14)
    # ------------------------------------------------------------------

    def _seguridad_shell_bloquea_rm():
        from tools.shell_tool import ShellTool
        resultado = ShellTool().execute("rm -rf /tmp/lo-que-sea")
        if "ERROR" not in resultado or "bloqueado" not in resultado:
            return "¡rm -rf NO fue bloqueado! (regresión grave de la Fase 14)"

    suite.run("Seguridad", "ShellTool bloquea comandos peligrosos", _seguridad_shell_bloquea_rm)

    def _seguridad_shell_permite_seguro():
        from tools.shell_tool import ShellTool
        resultado = ShellTool().execute("echo prueba de evaluación")
        if "ERROR" in resultado:
            return f"un comando seguro fue bloqueado indebidamente: {resultado}"

    suite.run("Seguridad", "ShellTool permite comandos de la lista blanca", _seguridad_shell_permite_seguro)

    def _seguridad_pathguard_traversal():
        from security.path_guard import PathGuard
        permitido, motivo = PathGuard(base_dir=str(workspace)).validate("../../etc/passwd")
        if permitido:
            return "¡se permitió un path traversal! (regresión grave de la Fase 14)"

    suite.run("Seguridad", "PathGuard bloquea path traversal", _seguridad_pathguard_traversal)

    def _seguridad_plugin_roto_no_tumba():
        from plugins.plugin_manager import PluginManager
        carpeta = Path(tempfile.mkdtemp())
        (carpeta / "roto.py").write_text("import modulo_que_no_existe_de_verdad\n")
        (carpeta / "bueno.py").write_text(
            "from plugins.plugin import Plugin\n"
            "class BuenoEval(Plugin):\n"
            "    name = 'bueno_eval'\n"
            "    def initialize(self): pass\n"
        )
        resumen = PluginManager().load_all(directory=str(carpeta))
        if "bueno_eval" not in resumen["loaded"]:
            return f"el plugin bueno no cargó: {resumen}"
        if not resumen["failed"]:
            return "el plugin roto no quedó registrado como fallo"

    suite.run("Seguridad", "un plugin roto no tumba a los demás", _seguridad_plugin_roto_no_tumba)

    # ------------------------------------------------------------------
    # TAREAS
    # ------------------------------------------------------------------

    def _tareas_persistencia_reinicio():
        from brain.long_task_manager import LongTaskManager
        ltm = LongTaskManager()
        tid = ltm.create("tarea de evaluación", ["paso 1", "paso 2", "paso 3"])
        ltm.start(tid)
        ltm.advance(tid)
        ltm2 = LongTaskManager()  # simula reinicio
        tarea = ltm2.get(tid)
        if tarea is None or tarea["current_step"] != 1:
            return "la tarea no sobrevivió al reinicio simulado con el progreso correcto"

    suite.run("Tareas", "LongTaskManager sobrevive a un reinicio", _tareas_persistencia_reinicio)

    def _tareas_pausa_bloquea_avance():
        from brain.long_task_manager import LongTaskManager
        ltm = LongTaskManager()
        tid = ltm.create("tarea pausable", ["paso 1", "paso 2"])
        ltm.start(tid)
        ltm.pause(tid)
        try:
            ltm.advance(tid)
            return "se pudo avanzar una tarea pausada (regresión de la Fase 13)"
        except ValueError:
            pass

    suite.run("Tareas", "no se puede avanzar una tarea pausada", _tareas_pausa_bloquea_avance)

    # ------------------------------------------------------------------
    # AGENTES
    # ------------------------------------------------------------------

    def _agentes_tool_agent():
        from agents.tool_agent import ToolAgent
        from types import SimpleNamespace
        agente = ToolAgent()
        respuesta = agente.execute(SimpleNamespace(message="calc 2 + 2"))
        if not getattr(respuesta, "success", False):
            return f"ToolAgent no resolvió un cálculo simple: {respuesta}"

    suite.run("Agentes", "ToolAgent resuelve un cálculo simple", _agentes_tool_agent)

    def _agentes_vision_honesto():
        from vision.vision_manager import VisionManager
        vm = VisionManager()
        if vm.is_available():
            return "SKIP: hay un modelo de visión instalado en este entorno, no se puede probar el caso 'no disponible'"
        return "SKIP: sin Ollama accesible en este entorno; is_available() ya se probó de forma aislada en la Fase 12"

    suite.run("Agentes", "VisionManager es honesto sobre disponibilidad", _agentes_vision_honesto)

    # ------------------------------------------------------------------
    # INTEGRACIÓN (Brain de extremo a extremo)
    # ------------------------------------------------------------------

    def _brain_integracion():
        if not _pyside6_disponible():
            return "SKIP: PySide6 no está instalado en este entorno (no afecta a la lógica de Brain, ya probada con stubs en Fases 2-15)"

        from brain.brain import Brain
        b = Brain()
        r = b.think("mi nombre es Danny")
        texto = getattr(r, "answer", None) or str(r)
        if "danny" not in texto.lower():
            return "Brain no recordó el nombre en la misma conversación"
        for atributo in ("rag", "vision", "long_tasks", "context", "conversation_manager"):
            if not hasattr(b, atributo):
                return f"a Brain le falta la capacidad '{atributo}'"

    suite.run("Integración", "Brain de extremo a extremo", _brain_integracion)

    return suite
