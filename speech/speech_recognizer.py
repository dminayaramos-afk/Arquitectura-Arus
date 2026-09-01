import json

class SpeechRecognizer:
    def __init__(self, model_path="models/vosk-es", sample_rate=16000):
        # Import diferido (Fase 11): antes esto estaba al nivel de
        # módulo, así que si vosk no estaba instalado, ni siquiera se
        # podía IMPORTAR arus.core.voice -- y main_window.py importa
        # arus.core.voice al arrancar. Un motor de voz no instalado no
        # debería poder impedir que la interfaz completa arranque
        # (punto 77 del prompt maestro: "no desactivar todo ARUS").
        try:
            from vosk import Model, KaldiRecognizer
        except ImportError as e:
            raise RuntimeError(
                "El reconocimiento de voz necesita el paquete 'vosk' "
                "instalado (pip install vosk) y un modelo en "
                f"'{model_path}'. La voz no está disponible, pero el "
                "resto de ARUS sí."
            ) from e

        self._KaldiRecognizer = KaldiRecognizer
        self.sample_rate = sample_rate
        self.model = Model(model_path)

    def transcribe_file(self, wav_path):
        import wave

        wf = wave.open(wav_path, "rb")

        if wf.getframerate() != self.sample_rate:
            raise ValueError("Frecuencia incorrecta")

        rec = self._KaldiRecognizer(self.model, self.sample_rate)

        while True:
            data = wf.readframes(4000)
            if not data:
                break
            rec.AcceptWaveform(data)

        return json.loads(rec.FinalResult()).get("text", "")
