# ARUS

**Asistente de IA con interfaz visual estilo HUD de ciencia ficción y un
"Brain" central que decide qué hacer a partir de lenguaje natural — sin
menús, como hablar con ChatGPT, pero con memoria propia, herramientas
reales y un cuerpo visual.**

ARUS está pensado como un **cuerpo**: la interfaz, la memoria, las
herramientas y la seguridad funcionan igual sin importar qué IA haya
detrás. Puedes conectarlo a [Ollama](https://ollama.com), a
[LM Studio](https://lmstudio.ai/), a `llama.cpp`, o a cualquier motor
local que hable el protocolo estilo OpenAI — una IA, varias a la vez, o
ninguna todavía. Ver [`docs/CONECTAR_IA.md`](docs/CONECTAR_IA.md).

## Qué hace

- **Conversación en lenguaje natural, sin menús.** El "Brain"
  (`brain/brain.py`) interpreta lo que escribes y decide qué módulo
  usar (chat con IA, un comando, una herramienta) en vez de obligarte a
  navegar opciones.
- **Memoria real y persistente**, no solo el historial de la sesión:
  memoria de largo plazo, preferencias de usuario, memoria semántica y de
  tareas (`memory/`).
- **Herramientas que la IA puede usar de verdad** durante la
  conversación (`tools/`): calculadora, archivos, git (solo lectura),
  ejecutar tests, búsqueda web real, capturas de pantalla, y más — con un
  planificador y un verificador (`brain/planner.py`,
  `brain/verifier.py`) que revisan el resultado y reintentan si algo
  falla.
- **Seguridad activa, no decorativa**: los comandos de shell y el acceso
  a archivos pasan por `security/shell_guard.py` y
  `security/path_guard.py`, que de verdad restringen lo que se puede
  ejecutar y a qué rutas se puede acceder — no son una promesa en un
  comentario.
- **Tareas autónomas** que sobreviven a un reinicio de la aplicación
  (`brain/long_task_manager.py`).
- **RAG** (recuperación aumentada) para consultar documentos propios
  (`rag/`), con embeddings ligeros que no necesitan descargar modelos
  ni conexión a internet.
- **Voz**: reconocimiento de voz con Vosk (`arus/core/voice.py`) y texto
  a voz con `espeak-ng` (`arus/voice/tts_provider.py`), con carga
  perezosa para que la aplicación arranque igual aunque no tengas estas
  dependencias instaladas.
- **Plugins**: se pueden añadir herramientas nuevas dejando un módulo en
  `plugins/installed/`, sin tocar el núcleo (`plugins/plugin_manager.py`).
- **Evaluación automática**: una batería de más de 30 pruebas reales
  (`evaluation/`) que cubre memoria, herramientas, seguridad, tareas,
  agentes e integración de extremo a extremo — pensada para ejecutarse
  antes y después de cualquier cambio importante.

## Instalación

Requiere **Python 3.11+**.

```bash
git clone https://github.com/dminayaramos-afk/Arquitectura-Arus.git
cd Arquitectura-Arus
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Dependencias del sistema (no son paquetes de Python)

- **PySide6** necesita Qt6; en Linux normalmente basta con `pip install
  PySide6`, pero en algunas distros hace falta instalar además
  librerías del sistema (`libxcb`, etc. — busca "PySide6 <tu distro>" si
  falla al importar).
- **Voz (opcional):**
  - Reconocimiento de voz: descarga un [modelo de Vosk en
    español](https://alphacephei.com/vosk/models) y colócalo en
    `models/vosk-es/` (o donde indique tu configuración).
  - Texto a voz: instala `espeak-ng` con el gestor de paquetes de tu
    sistema (`sudo apt install espeak-ng` en Debian/Ubuntu/MX Linux).
  - Si no instalas ninguna de las dos, ARUS arranca igual: la voz
    simplemente no está disponible.
- **Una IA (opcional pero recomendable):** [Ollama](https://ollama.com)
  o cualquier otro motor local. Ver la siguiente sección.

## Conectar una IA

Por defecto ARUS **no asume ninguna IA** y no arranca ningún proceso por
su cuenta. Para conectar una (o varias), edita `config/settings.json`:

```json
{
    "ai_provider": "ollama",
    "ai_providers": {
        "ollama": {
            "type": "ollama",
            "host": "http://127.0.0.1:11434",
            "model": "qwen3:4b",
            "auto_start": true
        }
    }
}
```

Guía completa, con ejemplos para LM Studio y cómo añadir un motor nuevo,
en [`docs/CONECTAR_IA.md`](docs/CONECTAR_IA.md).

## Ejecutar

```bash
python3 run.py
```

## Estructura del proyecto

```text
Arquitectura-Arus/
├── arus/
│   ├── main.py            # Punto de entrada real (lanza la interfaz)
│   ├── interface/          # Interfaz gráfica (PySide6)
│   ├── core/, devices/, voice/   # Perfil de dispositivo, voz, utilidades del núcleo
├── brain/                  # Brain central: interpretación, planificador, verificador, tareas largas
├── ai/                     # ModelManager + proveedores de IA (Ollama, compatible con OpenAI...)
├── memory/                 # Memoria persistente (largo plazo, semántica, preferencias, tareas)
├── tools/                  # Herramientas que la IA puede ejecutar
├── security/                # ShellGuard, PathGuard — restricciones reales, no decorativas
├── skills/                  # Skills conectadas al Brain (chat con IA, etc.)
├── rag/                     # Recuperación aumentada sobre documentos propios
├── plugins/                 # Sistema de plugins (herramientas externas)
├── evaluation/               # Batería de pruebas end-to-end del proyecto completo
├── tests/                    # Tests unitarios
├── docs/                     # Documentación (conectar IA, arquitectura...)
├── config/                    # Configuración (config/settings.json)
└── run.py                    # Atajo para lanzar arus/main.py
```

## Tests

```bash
pip install pytest
pytest tests/
python3 tests/test_tools.py
python3 -c "from evaluation.suite import run_all; print(run_all().report())"
```

## Estado del proyecto y limitaciones conocidas

ARUS se desarrolla por fases, documentadas en los `LEEME_FASE*.md` de la
raíz del repositorio (historial de desarrollo). Estado honesto a día de
hoy:

- El chat por texto con IA está conectado de extremo a extremo
  (interfaz → Brain → proveedor de IA). La voz (STT/TTS) existe como
  módulos independientes pero **todavía no está cableada** al flujo de
  conversación principal.
- La visión (analizar una imagen) tiene infraestructura real
  (`vision/`), pero la interfaz aún no tiene ningún control para
  adjuntar una imagen, y el modelo por defecto configurado no es
  multimodal.
- `git commit`/`git push` desde ARUS están **deshabilitados a
  propósito**: la herramienta de git es de solo lectura porque la IA no
  debería poder autorizarse a sí misma a modificar el historial del
  repositorio sin confirmación humana explícita, y esa confirmación
  todavía no existe.
- Hay un subsistema completo (`arus/laboratory/`) que existe en el
  código pero no está conectado al núcleo — trabajo en curso / pendiente
  de decidir si se integra.
- Existen dos módulos huérfanos (`verification/`, `planning/`) que
  duplican funciones ya cubiertas por `brain/verifier.py` y
  `brain/planner.py`; están pendientes de fusionar o retirar.

Nada de esto está oculto ni fingido: cada fase de desarrollo se ha
probado de verdad (no solo "compila") antes de darse por completada, y
las carencias se han dejado documentadas en vez de simuladas.

## Autor

Creado por **Danny Jesús Minaya Ramos**.
