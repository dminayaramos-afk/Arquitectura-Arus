"""
ARUS
Speaker (Fase 11)

Antes: hablaba con espeak-ng directamente y con `flatpak-spawn --host`
antepuesto siempre, sin comprobar si tenía sentido (bug real: rompía
en cualquier sistema sin Flatpak, incluido Windows -- el hardware de
referencia del proyecto). Nada en el proyecto la usaba todavía
(auditado antes de tocarla).

Ahora: delega en un TTSProvider (punto 28) y soporta interrupción
(punto 29). La firma pública `Speaker().speak(text)` se mantiene
igual para no romper nada que la use en el futuro.
"""

from __future__ import annotations

from typing import Optional

from arus.voice.tts_provider import TTSProvider, EspeakProvider
from arus.voice.text_cleaner import clean_for_speech


class Speaker:

    def __init__(self, provider: Optional[TTSProvider] = None):

        self.provider = provider or EspeakProvider()

        self._proceso_actual = None

    def speak(self, text: str):

        print("ARUS:", text)

        if not self.provider.is_available():
            print("Voz no disponible: no se encontró un motor TTS instalado.")
            return

        texto_limpio = clean_for_speech(text)

        if not texto_limpio:
            return

        try:

            self._proceso_actual = self.provider.speak(texto_limpio)

        except Exception as e:

            print("Error voz:", e)

    def stop(self):
        """
        Voz interrumpible (punto 29): para usar cuando un VAD
        detecte que el usuario ha empezado a hablar. La detección de
        voz en sí (VAD) no se implementa en esta fase -- necesita
        audio en streaming y una librería no confirmada en el
        proyecto (ver informe de la Fase 11); esto deja el mecanismo
        de parada listo para cuando exista.
        """

        if self._proceso_actual is not None and self._proceso_actual.poll() is None:

            try:
                self._proceso_actual.terminate()
            except Exception:
                pass

    def is_speaking(self) -> bool:

        return self._proceso_actual is not None and self._proceso_actual.poll() is None
