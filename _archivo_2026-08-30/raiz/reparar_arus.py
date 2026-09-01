import os
import subprocess


archivos = {

"arus/voice/speaker.py": r'''
import subprocess
import shutil

class Speaker:

    def speak(self,text):

        print("ARUS:",text)

        if shutil.which("espeak-ng"):
            subprocess.Popen(
                ["espeak-ng", text]
            )
            return

        subprocess.Popen(
            [
                "flatpak-spawn",
                "--host",
                "espeak-ng",
                text
            ]
        )
''',


"arus/voice/recognizer.py": r'''
import speech_recognition as sr
import subprocess
import os
import time


class Recognizer:

    def __init__(self):
        self.rec=sr.Recognizer()


    def listen(self):

        print("ARUS escuchando")

        archivo=os.path.expanduser(
            "~/ARUS/tmp/voz.wav"
        )

        os.makedirs(
            os.path.dirname(archivo),
            exist_ok=True
        )


        try:

            subprocess.run(
                [
                    "flatpak-spawn",
                    "--host",
                    "bash",
                    "-c",
                    f"arecord -d 5 -f S16_LE -r 16000 -c 1 {archivo}"
                ],
                check=True
            )


            time.sleep(1)


            with sr.AudioFile(archivo) as source:

                audio=self.rec.record(source)


            texto=self.rec.recognize_google(
                audio,
                language="es-ES"
            )


            print("Usuario:",texto)

            return texto


        except Exception as e:

            print(
                "Error voz:",
                repr(e)
            )

            return ""
''',


"arus/voice/__init__.py": r'''
from .speaker import Speaker
from .recognizer import Recognizer

__all__=[
"Speaker",
"Recognizer"
]
'''
}


for ruta,contenido in archivos.items():

    os.makedirs(
        os.path.dirname(ruta),
        exist_ok=True
    )

    with open(ruta,"w") as f:
        f.write(contenido)


print("ARUS reparado")


print("Probando voz...")

subprocess.run(
[
"python3",
"-c",
"from arus.voice.speaker import Speaker; Speaker().speak('ARUS sistema activo')"
]
)
