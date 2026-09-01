"""
ARUS
Screenshot Tool (Fase 12, punto 26: "capturas de pantalla")

A diferencia del resto de Visión, esto SÍ se puede usar hoy mismo a
través del ciclo de herramientas de la Fase 6 (function-calling) --
capturar pantalla no necesita un modelo multimodal, solo Pillow (ya
está instalado en el proyecto). Analizar lo capturado con
VisionManager sigue dependiendo de tener un modelo de visión
instalado en Ollama.
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path

from tools.base_tool import BaseTool

CARPETA_CAPTURAS = Path("tmp/capturas")


class ScreenshotTool(BaseTool):

    name = "screenshot"

    description = "Captura la pantalla actual y guarda la imagen en disco."

    parameters = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    def execute(self):

        try:
            from PIL import ImageGrab
        except ImportError:
            return "ERROR: Pillow no está instalado (pip install Pillow)."

        try:

            imagen = ImageGrab.grab()

        except Exception as e:

            return (
                f"ERROR: no se pudo capturar la pantalla ({e}). "
                "Puede que no haya un entorno gráfico disponible."
            )

        CARPETA_CAPTURAS.mkdir(parents=True, exist_ok=True)

        nombre = f"{int(time.time())}_{uuid.uuid4().hex[:8]}.png"

        ruta = CARPETA_CAPTURAS / nombre

        imagen.save(ruta)

        return str(ruta)
