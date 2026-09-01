"""
ARUS - Artificial Reasoning Unified System
------------------------------------------

Gestión centralizada de rutas del proyecto.
"""

from pathlib import Path

# Directorio raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parent.parent

# Directorios principales
CORE_DIR = ROOT_DIR / "core"
BRAIN_DIR = ROOT_DIR / "brain"
CONFIG_DIR = ROOT_DIR / "config"
LOGS_DIR = ROOT_DIR / "logs"
DATA_DIR = ROOT_DIR / "data"
TESTS_DIR = ROOT_DIR / "tests"

# Archivos principales
SETTINGS_FILE = CONFIG_DIR / "settings.json"
LOG_FILE = LOGS_DIR / "arus.log"
