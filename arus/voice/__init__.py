from .speaker import Speaker

__all__ = ["Speaker"]

try:
    # Recognizer (STT por vosk) es opcional: si vosk no está
    # instalado, el resto de arus.voice (Speaker/TTS, que no depende
    # de vosk) no debe dejar de funcionar por eso. Antes, este import
    # sin proteger rompía TODO el paquete -- incluida la voz de
    # salida -- solo por no tener vosk instalado.
    from .recognizer import Recognizer
    __all__.append("Recognizer")
except ImportError:
    Recognizer = None
