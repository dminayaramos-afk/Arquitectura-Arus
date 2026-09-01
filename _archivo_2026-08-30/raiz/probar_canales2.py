import wave
import audioop

wf = wave.open("tmp/prueba_voz.wav", "rb")

print("Canales:", wf.getnchannels())

data = wf.readframes(wf.getnframes())

izq = audioop.tomono(data, wf.getsampwidth(), 1, 0)
der = audioop.tomono(data, wf.getsampwidth(), 0, 1)

print("Nivel izquierdo:", audioop.rms(izq, wf.getsampwidth()))
print("Nivel derecho:", audioop.rms(der, wf.getsampwidth()))
