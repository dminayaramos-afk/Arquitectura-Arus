"""
ARUS
TTS Provider (Fase 11, punto 28 del prompt maestro)

"Convertir Speaker en una abstracción: Speaker -> TTS Provider ->
espeak-ng / futuro motor TTS. El resto del sistema no debe depender
directamente de espeak-ng."

Bug real corregido de paso: `arus/voice/speaker.py` anteponía
SIEMPRE `flatpak-spawn --host` al comando, sin comprobar si ARUS
estaba realmente corriendo dentro de un sandbox Flatpak. El hardware
de referencia del prompt maestro (punto 68) es un ASUS X550L con
Windows -- ahí `flatpak-spawn` no existe, así que la voz nunca habría
funcionado. Ahora solo se antepone si `FLATPAK_ID` está presente en
el entorno (la forma estándar en que una app Flatpak detecta que
corre dentro de su propio sandbox).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from typing import Optional


class TTSProvider(ABC):

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def speak(self, text: str) -> Optional[subprocess.Popen]:
        """Debe devolver el proceso lanzado (para poder interrumpirlo,
        punto 29), o None si no pudo hablar."""
        ...


class EspeakProvider(TTSProvider):

    def __init__(self, voz: str = "es", velocidad: int = 150):

        self.voz = voz
        self.velocidad = velocidad

    def _binario(self) -> Optional[str]:

        return shutil.which("espeak-ng") or shutil.which("espeak")

    def is_available(self) -> bool:

        return self._binario() is not None

    def _dentro_de_flatpak(self) -> bool:

        return "FLATPAK_ID" in os.environ

    def speak(self, text: str) -> Optional[subprocess.Popen]:

        binario = self._binario()

        if binario is None:
            return None

        comando = [binario, "-v", self.voz, "-s", str(self.velocidad), text]

        if self._dentro_de_flatpak():
            comando = ["flatpak-spawn", "--host"] + comando

        return subprocess.Popen(
            comando,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
