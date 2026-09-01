# Conectar una o varias IAs a ARUS

ARUS es un **cuerpo**: la interfaz, la memoria, las herramientas, la
seguridad... todo eso funciona igual sin importar a qué IA esté
conectado. Antes esto no era cierto del todo: la app arrancaba (y mataba
y relanzaba) Ollama a la fuerza en cada inicio, aunque no lo hubieras
pedido. Eso ya no pasa. Por defecto, **ARUS no arranca ni asume ninguna
IA**: hasta que configures una, responde con un aviso claro en vez de
fallar.

## Configurar una IA

Edita `config/settings.json`:

```json
{
    "ai_provider": "ollama",
    "ai_providers": {
        "ollama": {
            "type": "ollama",
            "host": "http://127.0.0.1:11434",
            "model": "qwen3:4b",
            "auto_start": false
        }
    }
}
```

- `ai_provider`: cuál usar por defecto cuando no se especifica ninguna
  explícitamente (usa la clave, no el "type").
- `ai_providers`: un diccionario con **una o varias** IAs. Cada entrada
  tiene el nombre que tú le des (`"ollama"`, `"lmstudio"`, `"trabajo"`...
  lo que quieras) y dentro:
  - `type`: `"ollama"` o `"openai_compatible"` (ver tipos soportados
    abajo).
  - `host` / `model`: dónde está y qué modelo usar.
  - `auto_start` (solo aplica a `type: "ollama"`): si es `true`, ARUS
    arranca (y al cerrar, apaga) el proceso de Ollama por ti. Si es
    `false` o no está, asume que tú ya lo tienes corriendo, o que no lo
    necesitas.

## Tipos de proveedor soportados

### `"ollama"`

Habla con [Ollama](https://ollama.com) por su cliente Python oficial.
Incluye llamada a herramientas (tools) integrada con
`Planner`/`TaskManager`/`Verifier`, así que la IA puede ejecutar acciones
reales de ARUS (calculadora, archivos, git, etc.) durante la
conversación.

### `"openai_compatible"`

Habla con **cualquier** motor local que exponga la API estilo OpenAI
(`POST /chat/completions`) — que es prácticamente el estándar de facto
fuera de Ollama:

- [LM Studio](https://lmstudio.ai/) (activa "Local Server" y usa
  `http://127.0.0.1:1234/v1`)
- `llama.cpp` con `./server` en modo compatible con OpenAI
- [koboldcpp](https://github.com/LostRuins/koboldcpp) (su endpoint
  `/v1`)
- text-generation-webui con la extensión `openai`
- vLLM, LocalAI, y en general casi cualquier motor de inferencia local
  moderno

Ejemplo con LM Studio:

```json
"lmstudio": {
    "type": "openai_compatible",
    "host": "http://127.0.0.1:1234/v1",
    "model": "el-nombre-del-modelo-cargado"
}
```

Si algún día quieres usar un servicio remoto real (OpenAI, un proveedor
compatible en la nube, etc.), el mismo tipo `"openai_compatible"` sirve
añadiendo `"api_key": "..."` a la configuración de esa entrada.

## Varias IAs a la vez

Puedes tener varias entradas en `ai_providers` simultáneamente. Todas se
conectan (o se intentan) al arrancar ARUS; si una falla (no está
encendida, falta una dependencia, etc.) se salta con un aviso en la
consola y las demás siguen funcionando con normalidad — nunca revienta
toda la aplicación por un proveedor caído.

Para pedir una IA concreta en vez de la de por defecto, en código:

```python
from ai.model_manager import ModelManager

mm = ModelManager()
mm.generate("hola", provider="lmstudio")   # fuerza esa IA en concreto
mm.generate("hola")                         # usa la de "ai_provider"
```

## Añadir un motor nuevo

Si en el futuro quieres soportar un tipo de motor que no hable ni el
protocolo de Ollama ni el compatible con OpenAI:

1. Crea `ai/providers/mi_proveedor.py` con una clase que herede de
   `BaseProvider` (`ai/providers/base_provider.py`) e implemente
   `generate(self, prompt, history=None) -> str`.
2. Regístrala en `PROVIDER_TYPES` dentro de `ai/provider_factory.py`.
3. Úsala en `config/settings.json` con `"type": "mi_proveedor"`.

Nada más del proyecto (interfaz, Brain, skills) necesita cambiar: todos
pasan por `ModelManager`, que no sabe ni le importa qué IA hay detrás.
