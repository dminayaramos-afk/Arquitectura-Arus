"""
ARUS - Interface Controller Unificado (Fases 39-44)
Conecta la interfaz gráfica con el Cerebro, Skills y Commands nativos de ARUS.
"""

import sys
import os

# Aseguramos rutas para encontrar los módulos raíz del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from brain.brain import Brain
except ImportError:
    Brain = None

try:
    from commands.command_manager import CommandManager
except ImportError:
    CommandManager = None

try:
    from skills.skill_manager import SkillManager
except ImportError:
    SkillManager = None

class ARUSController:
    def __init__(self, core=None):
        self.core = core
        
        # Inicializamos los subsistemas nativos de ARUS
        self.skills = SkillManager() if SkillManager else None
        self.brain = Brain() if Brain else None
        if self.brain and self.skills:
            self.brain.skills = self.skills
            
        self.commands = CommandManager(brain=self.brain, skills=self.skills) if CommandManager else None

    def process(self, text: str) -> str:
        text_raw = text.strip()
        text_lower = text_raw.lower()
        
        # 1. Si existen comandos nativos registrados en ARUS, intentamos ejecutarlos primero
        if self.commands:
            try:
                # CommandManager.execute() (NO .handle(), que no existe --
                # ese era el bug: la llamada anterior a .handle() lanzaba
                # AttributeError en cada mensaje, silenciado por el
                # except:pass de abajo, así que ningún comando "/..."
                # se ejecutaba nunca).
                res_cmd = self.commands.execute(text_raw)
                if res_cmd:
                    return str(res_cmd)
            except Exception:
                pass

        # 2. Procesamiento a través del Cerebro y razonamiento autónomo (Fase 40 / 42)
        if self.brain:
            try:
                response = self.brain.think(text_raw)
                if hasattr(response, "answer"):
                    return response.answer
                return str(response)
            except Exception as e:
                return f"Error en el cerebro de ARUS: {e}"

        return f"ARUS [Sistema Operativo Activo]: Comando recibido -> {text_raw}"
