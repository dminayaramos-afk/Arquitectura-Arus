"""
ARUS
Voice Core (Fase 11)

Es el que de verdad usa `arus/interface/main_window.py`
(`self.voice = VoiceCore()`), pero el botón de voz de la interfaz
comprobaba `hasattr(self.voice, "start")` y esta clase nunca tuvo un
método `start()` -- así que el botón no hacía nada (auditado antes de
tocar nada: confirmado que `toggle_voice()` en main_window.py, que no
se toca en esta fase, es exactamente así). Se añade `start()` sin
tocar la interfaz, para que ese botón deje de ser un no-op.

Bug real corregido de paso: el comando de `ffmpeg` anteponía siempre
`flatpak-spawn --host` y usaba `-f pulse` (específico de Linux con
PulseAudio) sin comprobar el sistema operativo real -- en el hardware
de referencia del proyecto (Windows, punto 68) esto no habría
funcionado nunca. Ahora se detecta el sistema operativo y solo se usa
`flatpak-spawn` dentro de un sandbox Flatpak real.

Limitación honesta: no hay micrófono ni ffmpeg con dispositivo de
audio en el entorno donde se desarrolló y probó esto, así que la
captura de audio real NO se pudo verificar de extremo a extremo (ver
LEEME_FASE11.md). Lo que sí se probó es que `start()` no bloquea el
hilo principal y que la selección de comando por sistema operativo es
correcta.
"""

from __future__ import annotations

import os
import platform
import subprocess
import threading
import uuid
from typing import Callable, Optional

from speech import SpeechRecognizer


class VoiceCore:

    def __init__(
        self,
        on_result: Optional[Callable[[str], None]] = None,
        duracion_segundos: int = 5,
    ):

        # Creación diferida (Fase 11): antes `SpeechRecognizer()` se
        # instanciaba aquí mismo, y como necesita vosk, y
        # main_window.py hace `self.voice = VoiceCore()` SIN
        # try/except al construir la ventana principal, si vosk no
        # estaba instalado toda la interfaz de ARUS fallaba al
        # arrancar -- no solo la voz. Ahora VoiceCore() nunca falla;
        # el error (claro, no un traceback) solo aparece si de verdad
        # se intenta escuchar sin tener vosk instalado.
        self._recognizer = None

        self.on_result = on_result

        self.duracion_segundos = duracion_segundos

        self._escuchando = False

    @property
    def recognizer(self):

        if self._recognizer is None:
            self._recognizer = SpeechRecognizer()

        return self._recognizer

    def _dentro_de_flatpak(self) -> bool:

        return "FLATPAK_ID" in os.environ

    def _comando_grabacion(self, wav: str) -> list:

        sistema = platform.system()

        if sistema == "Windows":
            entrada = ["-f", "dshow", "-i", "audio=default"]
        elif sistema == "Darwin":
            entrada = ["-f", "avfoundation", "-i", ":0"]
        else:
            entrada = ["-f", "pulse", "-i", "default"]

        comando = [
            "ffmpeg", "-y", *entrada,
            "-t", str(self.duracion_segundos),
            "-ac", "1", "-ar", "16000",
            wav,
        ]

        if self._dentro_de_flatpak():
            comando = ["flatpak-spawn", "--host"] + comando

        return comando

    def listen(self) -> str:

        os.makedirs("tmp", exist_ok=True)

        wav = f"tmp/{uuid.uuid4().hex}.wav"

        try:
            subprocess.run(
                self._comando_grabacion(wav),
                check=True,
                capture_output=True,
            )

            return self.recognizer.transcribe_file(wav)

        finally:
            if os.path.exists(wav):
                os.remove(wav)

    def start(self):
        """
        Punto de enganche para el botón de voz de la interfaz
        (main_window.py comprueba `hasattr(self.voice, "start")`).
        Corre en un hilo aparte para no congelar la GUI (punto 46).

        No conecta el texto reconocido con Brain/ARUSController: main_window.py
        instancia `VoiceCore()` sin pasarle el controller, y no se
        toca la interfaz en esta fase para añadir ese cableado. El
        resultado llega a `on_result` si se proporcionó uno al crear
        VoiceCore (para cuando el propietario decida conectar el
        botón de verdad); si no, solo se imprime, igual que hacía
        `arus/voice/recognizer.py` antes de esta fase.
        """

        if self._escuchando:
            return

        def _tarea():

            self._escuchando = True

            try:

                texto = self.listen()

                print("Usuario (voz):", texto)

                if self.on_result:
                    self.on_result(texto)

            except Exception as e:

                print("Error al escuchar:", e)

            finally:

                self._escuchando = False

        threading.Thread(target=_tarea, daemon=True).start()

    def is_listening(self) -> bool:

        return self._escuchando
