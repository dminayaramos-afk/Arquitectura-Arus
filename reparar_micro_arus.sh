#!/bin/bash

echo "=== ARUS DIAGNOSTICO MICRO ==="

echo ""
echo "Dispositivos ALSA:"
flatpak-spawn --host arecord -l

echo ""
echo "Fuentes PipeWire/Pulse:"
flatpak-spawn --host pactl list short sources

echo ""
echo "Probando grabacion..."
mkdir -p tmp

flatpak-spawn --host arecord \
-D default \
-d 5 \
-f S16_LE \
-r 16000 \
-c 1 \
tmp/test_micro.wav

echo ""
echo "Analizando volumen..."

python3 - <<'PY'
import wave
import audioop

try:
    wf = wave.open("tmp/test_micro.wav","rb")
    data = wf.readframes(wf.getnframes())
    nivel = audioop.rms(data,wf.getsampwidth())

    print("Nivel micro:", nivel)

    if nivel == 0:
        print("ERROR: micro sin señal")
    elif nivel < 300:
        print("AVISO: señal muy baja")
    else:
        print("OK: micro funcionando")

except Exception as e:
    print("Error:",e)
PY

echo ""
echo "Reproduciendo prueba..."
flatpak-spawn --host aplay tmp/test_micro.wav

echo ""
echo "=== FIN ARUS MICRO ==="
