import wave
import json
import audioop
from vosk import Model, KaldiRecognizer

print("Cargando modelo...")
model = Model("models/vosk-es")

wf = wave.open("tmp/hw.wav","rb")

print("Canales:", wf.getnchannels())
print("Frecuencia:", wf.getframerate())
print("Frames:", wf.getnframes())

rec = KaldiRecognizer(
    model,
    16000
)

texto = ""

while True:

    data = wf.readframes(4000)

    if not data:
        break

    if wf.getnchannels() == 2:
        data = audioop.tomono(
            data,
            wf.getsampwidth(),
            0.5,
            0.5
        )

    if rec.AcceptWaveform(data):
        r = json.loads(rec.Result())
        texto += r.get("text","")


r = json.loads(rec.FinalResult())
texto += r.get("text","")

print("================")
print("RESULTADO:")
print(texto)
print("================")
