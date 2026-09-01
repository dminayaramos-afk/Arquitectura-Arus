# ARUS — Ollama desactivado por defecto + soporte real multi-IA (2026-08-30, sesión 2)

Pediste: "arus es un cuerpo para conectar con cualquier IA local o no, así
que solo desactiva ollama y ponle para que se pueda conectar una o
varias". Esto es lo que se hizo, verificado de verdad (no solo
compilado): tests 16/16 OK, test_tools.py 13/13 OK, evaluation/suite.py
27/27 OK 0 fallos, e instanciación real de `ARUSWindow()` en modo
offscreen con PySide6 instalado.

## Antes vs ahora

**Antes:** `main_window.py` mataba (`pkill -9 ollama`) y relanzaba Ollama
sin preguntar en cada arranque de ARUS, sin importar si querías usar otra
IA o ninguna. Al cerrar, volvía a matar `ollama` a la fuerza aunque tú lo
tuvieras corriendo para otra cosa. `ModelManager()` sin argumentos siempre
creaba un `LocalProvider` (Ollama) hardcodeado.

**Ahora:** por defecto (`"ai_provider": "none"` en `config/settings.json`,
que ya era el valor por defecto que tenías puesto pero que el código
ignoraba) ARUS **no toca ningún proceso ni asume ninguna IA**. Arranca en
0.33s en vez de 2s+. Si le pides algo a la IA sin haber configurado
ninguna, responde con un aviso claro en vez de fallar en silencio o
reventar.

## Cómo conectar una IA (o varias)

Todo explicado con ejemplos en **`docs/CONECTAR_IA.md`**. Resumen:

- `config/settings.json` tiene ahora una sección `ai_providers` donde
  defines una o varias IAs (cada una con nombre, `type`, host, modelo).
- Dos tipos soportados ya mismo:
  - `"ollama"` — el que ya tenías, ahora con host/modelo configurables
    en vez de fijos en el código, y con `auto_start` opcional (si lo
    pones a `true`, ARUS vuelve a gestionar el proceso de Ollama por ti,
    igual que antes, pero porque tú lo pediste, no por defecto).
  - `"openai_compatible"` — nuevo. Habla con **cualquier** motor local
    que use la API estilo OpenAI: LM Studio, llama.cpp server,
    koboldcpp, text-generation-webui, vLLM, LocalAI... prácticamente
    todo lo que no es Ollama usa este mismo formato, así que con un solo
    proveedor genérico ARUS puede conectarse a cualquiera de ellos sin
    necesitar una integración distinta para cada programa.
- Puedes tener varias IAs configuradas a la vez y elegir cuál usar por
  llamada (`ModelManager().generate("hola", provider="lmstudio")`), o
  dejar la de por defecto. Si una falla al conectar (apagada, falta una
  dependencia), se salta con un aviso y las demás siguen funcionando —
  nunca tumba toda la app.
- Añadir un motor nuevo que no hable ninguno de esos dos protocolos: una
  clase nueva heredando de `BaseProvider` + una línea en
  `ai/provider_factory.py`. Nada más del proyecto necesita cambiar.

## Un bug que la propia prueba real detectó (y se corrigió antes de entregar)

Mi primera versión de `ai/provider_factory.py` importaba el módulo del
proveedor Ollama (y por tanto el paquete `ollama`) de forma incondicional
al cargarse, aunque no lo estuvieras usando. Eso significaba que si algún
día el paquete `ollama` no estuviera instalado, ARUS fallaría al arrancar
aunque tú solo quisieras usar LM Studio. Lo pilló la propia prueba
de instanciación real en este entorno (aquí no está instalado el paquete
`ollama`). Se corrigió con imports perezosos: cada tipo de proveedor solo
se importa de verdad cuando hace falta construirlo.

## Otro ajuste de seguridad

`destruir_ollama_completo()` (se llama al cerrar ARUS) antes mataba
`ollama` a la fuerza sin condición. Ahora solo lo hace si fue el propio
ARUS quien lo arrancó (`self.ollama_process` no es `None`) — si ya lo
tenías corriendo por tu cuenta, o usas otra IA, ARUS ya no lo toca al
cerrar.

## Limpieza adicional

`ai/ollama_manager.py` — una clase huérfana (nada la usaba) con una ruta
de Ollama hardcodeada al estilo Flatpak (`/run/host/usr/local/bin/ollama`)
que ya no tenía sentido con el nuevo sistema. Archivada, no borrada
(`_archivo_2026-08-30/raiz/ollama_manager.py.huerfano`).

## Archivos nuevos

- `ai/providers/openai_compatible_provider.py`
- `ai/providers/none_provider.py`
- `ai/provider_factory.py`
- `docs/CONECTAR_IA.md`

## Archivos modificados (con backup del original en `_backup_antes_multi_ia_20260830/`)

- `arus/interface/main_window.py` — arranque/cierre de Ollama ahora
  condicionados a la configuración, ya no automáticos.
- `ai/model_manager.py` — sin proveedores explícitos, construye desde
  `config/settings.json` en vez de asumir Ollama.
- `ai/providers/local_provider.py` — `host` ahora configurable (antes
  fijo a `127.0.0.1:11434`).
- `config/settings.json` / `config/settings.py` — nueva sección
  `ai_providers`.

## Aplicar a tu repo

Igual que la limpieza anterior: descomprime este zip sobre tu copia local
y copia el contenido. Como antes, no incluye `_backup_*`, `ARUS_BACKUP`
ni `models/` (sin cambios, ya los tienes).

Después, para volver a usar Ollama tal y como lo tenías, solo tienes que
poner en `config/settings.json`:

```json
"ai_provider": "ollama",
"ai_providers": {
    "ollama": {
        "type": "ollama",
        "host": "http://127.0.0.1:11434",
        "model": "qwen3:4b",
        "auto_start": true
    }
}
```

(`auto_start: true` es lo que le devuelve a ARUS el comportamiento de
antes: arrancarlo y apagarlo él solo.)
