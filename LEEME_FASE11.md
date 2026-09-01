# ARUS MARK 7 — FASE 11: Voz

## Como instalar
Sustituye/añade estos archivos (mismas rutas):

    arus/voice/__init__.py          (modificado)
    arus/voice/speaker.py           (modificado)
    arus/voice/tts_provider.py      (nuevo)
    arus/voice/text_cleaner.py      (nuevo)
    arus/core/voice.py              (modificado)
    speech/speech_recognizer.py     (modificado)

No se toco `arus/interface/*`.

## El bug mas grave que encontre en todo el proyecto hasta ahora
`arus/interface/main_window.py` (protegida, no se toca) hace
`self.voice = VoiceCore()` al construir la ventana principal, SIN
try/except. `VoiceCore.__init__` instanciaba `SpeechRecognizer()`,
que necesita el paquete `vosk` instalado -- y `vosk` NO esta
instalado en este proyecto. Es decir: **si alguien intentaba arrancar
ARUS tal cual sin haber instalado vosk, la interfaz entera fallaba al
abrir, no solo la voz.** Lo detecte al intentar probar mi propio
codigo (ni siquiera pude instanciar `VoiceCore()` en mis pruebas al
principio) y lo corregi haciendo perezosa la creacion del
`SpeechRecognizer` -- ahora `VoiceCore()` nunca falla; el error
(claro, no un traceback) solo aparece si de verdad se intenta
escuchar sin tener vosk instalado.

Relacionado: `speech/speech_recognizer.py` importaba `vosk` al nivel
de modulo, asi que ni siquiera se podia IMPORTAR
`arus.core.voice` (y por tanto tampoco `main_window.py`) sin vosk
instalado. Tambien lo hice perezoso (el import de vosk ahora ocurre
dentro de `__init__`, con un mensaje de error claro en vez de un
`ModuleNotFoundError` crudo).

Y `arus/voice/__init__.py` tenia el mismo problema con `Recognizer`
(otra clase de STT, ver mas abajo): si vosk faltaba, ni siquiera se
podia usar `Speaker` (que no necesita vosk para nada), porque el
`__init__.py` del paquete importaba ambas cosas juntas sin proteccion.

## Segundo bug real: todo el audio asumia Linux+Flatpak
`arus/voice/speaker.py` anteponia SIEMPRE `flatpak-spawn --host` al
comando de espeak-ng, y `arus/core/voice.py` hacia lo mismo con
ffmpeg usando `-f pulse` (especifico de PulseAudio/Linux). El hardware
de referencia del propio prompt maestro (punto 68) es un ASUS X550L
con Windows -- ahi ni `flatpak-spawn` existe ni `-f pulse` funciona.
La voz, tal como estaba escrita, no podia funcionar nunca en el
hardware real del proyecto. Corregido: `flatpak-spawn` solo se usa si
se detecta que ARUS esta corriendo de verdad dentro de un sandbox
Flatpak (variable de entorno `FLATPAK_ID`), y el comando de ffmpeg
elige el backend de audio segun el sistema operativo detectado
(`dshow` en Windows, `avfoundation` en macOS, `pulse` en Linux).

## Auditoria: tres implementaciones de STT duplicadas (no fusionadas)
Encontre `arus/voice/recognizer.py` (Recognizer, hardcodea rutas y
flatpak-spawn), `speech/speech_recognizer.py` (SpeechRecognizer, la
que SI usa `arus/core/voice.py`, la ruta viva) y
`arus/core/voice.py` (VoiceCore, la que de verdad importa
main_window.py). Solo la combinacion VoiceCore+SpeechRecognizer esta
conectada a algo real; `Recognizer` no la importa nadie (confirmado
antes de tocar nada). No la fusione ni la borre -- mismo criterio que
con los agentes duplicados de la Fase 6: es una decision de
arquitectura, no un fix incremental. Se deja para que decidas.

## Lo que SI se implemento (puntos 27-30 del prompt maestro)
- **TTS Provider (punto 28):** `Speaker` ya no depende directamente de
  espeak-ng; delega en un `TTSProvider` (`EspeakProvider` hoy,
  sustituible sin tocar `Speaker`).
- **Voz interrumpible (punto 29):** `Speaker.stop()` -- probado
  interrumpiendo un proceso real en marcha.
- **Limpieza de texto para voz (punto 30):**
  `arus/voice/text_cleaner.py` quita bloques de codigo, markdown,
  URLs largas antes de hablar.
- **Boton de voz de la interfaz deja de ser un no-op:**
  `main_window.py` comprueba `hasattr(self.voice, "start")` -- antes
  `VoiceCore` no tenia ese metodo, asi que el boton no hacia nada.
  Ahora si lo tiene, corre en un hilo aparte (no congela la GUI,
  punto 46) y transcribe.

## Lo que NO se hizo (honesto, no fingido)
- **VAD (deteccion de que el usuario empieza a hablar, punto 27/29):**
  necesita audio en streaming y una libreria (webrtcvad/silero-vad)
  no confirmada en el proyecto. `Speaker.stop()` deja el mecanismo de
  interrupcion listo, pero nada llama a `stop()` automaticamente
  todavia -- eso necesitaria el VAD real.
- **Streaming de respuesta hablada mientras se genera (punto 31):**
  no implementado en esta fase.
- **Voz -> Brain -> respuesta hablada, de punta a punta:**
  `main_window.py` crea `VoiceCore()` SIN pasarle el controller, y no
  se toca la interfaz en esta fase. `VoiceCore.start()` transcribe y
  lo imprime (y lo pasa a `on_result` si se lo das al construirlo),
  pero nada conecta ese texto con `ARUSController.process()` todavia.
  Conectarlo de verdad necesitaria una linea nueva en
  `main_window.py` (pasar `self.controller` a `VoiceCore`) -- te lo
  señalo para que decidas si autorizas ese cambio puntual o prefieres
  otra via.
- **Nada de esto se pudo probar con audio real:** no hay microfono,
  ni espeak-ng/vosk instalados, en el entorno donde desarrolle esto.
  Lo que si probe (10 casos reales): limpieza de texto, deteccion
  honesta de motor TTS ausente, seleccion correcta de comando segun
  SO, interrupcion real de un proceso, y sobre todo, que
  `VoiceCore()` YA NO ROMPE toda la interfaz si falta vosk.

## FASE 11 — RESULTADO

Archivos creados:
- arus/voice/tts_provider.py
- arus/voice/text_cleaner.py

Archivos modificados:
- arus/voice/__init__.py (import de Recognizer protegido)
- arus/voice/speaker.py (delega en TTSProvider, añade stop())
- arus/core/voice.py (start() nuevo, SpeechRecognizer perezoso, audio
  multiplataforma)
- speech/speech_recognizer.py (import de vosk perezoso)

Archivos NO modificados:
- arus/interface/* (identico byte a byte)
- arus/voice/recognizer.py (auditado, duplicado, no tocado -- ver
  seccion de arriba)

Pruebas: 10 casos reales, todos OK, incluyendo el hallazgo critico de
que `VoiceCore()` ya no puede tumbar el arranque de toda la interfaz.
Sin regresion en Fases 2-10. Interfaz identica byte a byte. Sintaxis
de todo el proyecto: OK. Arranque completo con PySide6/Ollama/vosk/
espeak-ng reales: NO VERIFICADO en este entorno (nada de eso esta
instalado aqui) -- confirmalo en tu maquina, es la fase donde mas
importa que lo hagas.

Pendiente: conectar voz->Brain->voz de punta a punta (necesita una
linea en main_window.py, ver arriba); VAD real; streaming de voz;
Fase 12 (Vision) en adelante hasta Fase 16; decisiones pendientes de
fases anteriores (agentes duplicados, cuando conectar RAG, mecanismo
de confirmacion humana para Git).
