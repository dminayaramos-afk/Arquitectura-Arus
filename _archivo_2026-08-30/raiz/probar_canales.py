import wave
import json
import audioop
from vosk import Model, KaldiRecognizer

model = Model("models/vosk-es")

wf = wave.open("tmp/voz.wav","rb")

print("canales", wf.getnchannels())

rec1 = KaldiRecognizer(model,16000)
rec2 = KaldiRecognizer(model,16000)

while True:
    data = wf.readframes(4000)

    if not data:
        break

    if wf.getnchannels()==2:
        izquierda = audioop.tomono(
            data,
            2,
            1,
            0
        )

        derecha = audioop.tomono(
            data,
            2,
            0,
            1
        )

        rec1.AcceptWaveform(izquierda)
        rec2.AcceptWaveform(derecha)

print("IZQUIERDA:")
print(json.loads(rec1.FinalResult())["text"])

print("DERECHA:")
print(json.loads(rec2.FinalResult())["text"])
