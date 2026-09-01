import subprocess
import os
import json
import wave

from vosk import Model, KaldiRecognizer


class Recognizer:


    def __init__(self):

        modelo = os.path.expanduser(
            "~/ARUS/models/vosk-es"
        )

        if not os.path.exists(modelo):

            raise Exception(
                "No existe modelo Vosk en ~/ARUS/models/vosk-es"
            )

        self.model = Model(modelo)



    def listen(self):

        print("ARUS escuchando...")


        wav = os.path.expanduser(
            "~/ARUS/tmp/voz.wav"
        )


        os.makedirs(
            os.path.dirname(wav),
            exist_ok=True
        )


        comando = (
            f"arecord "
            f"-D default "
            f"-d 6 "
            f"-f S16_LE "
            f"-r 16000 "
            f"-c 1 "
            f"{wav}"
        )


        subprocess.run(
            [
                "flatpak-spawn",
                "--host",
                "bash",
                "-c",
                comando
            ],
            check=True
        )


        wf = wave.open(
            wav,
            "rb"
        )


        rec = KaldiRecognizer(
            self.model,
            wf.getframerate()
        )


        texto = ""


        while True:

            data = wf.readframes(4000)


            if len(data) == 0:
                break


            if rec.AcceptWaveform(data):

                resultado = json.loads(
                    rec.Result()
                )

                texto += resultado.get(
                    "text",
                    ""
                )


        final = json.loads(
            rec.FinalResult()
        )


        texto += final.get(
            "text",
            ""
        )


        print(
            "Usuario:",
            texto
        )


        return texto
