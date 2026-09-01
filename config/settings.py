"""
ARUS - Artificial Reasoning Unified System
------------------------------------------

Gestión de la configuración del proyecto.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arus.core.paths import SETTINGS_FILE


class Settings:
    """Gestiona la configuración de ARUS."""

    DEFAULTS = {
        "language": "es",
        "theme": "dark",
        "ai_provider": "none",
        "ai_providers": {},
        "debug": False,
    }

    def __init__(self) -> None:
        self._data = self.DEFAULTS.copy()

    def load(self) -> None:
        """Carga la configuración desde disco."""
        if SETTINGS_FILE.exists():
            with SETTINGS_FILE.open("r", encoding="utf-8") as file:
                self._data.update(json.load(file))

    def save(self) -> None:
        """Guarda la configuración en disco."""
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with SETTINGS_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                self._data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Modifica un valor de configuración."""
        self._data[key] = value
