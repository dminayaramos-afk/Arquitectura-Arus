"""
ARUS
Fábrica de proveedores de IA

ARUS es un "cuerpo" pensado para conectarse a cualquier IA -- local o no,
una o varias -- sin que el código de la interfaz ni del cerebro (Brain)
tengan que saber nada de Ollama, LM Studio, ni de ningún motor concreto.

Este módulo lee `config/settings.json` y construye los proveedores que el
usuario haya configurado. Si no hay ninguno configurado (`ai_provider` es
`"none"`, el valor por defecto), ARUS no intenta arrancar ni conectar con
nada por su cuenta: responde con un mensaje claro (`NoneProvider`) en vez
de fallar en silencio o forzar Ollama como antes.

Formato de `config/settings.json`:

    {
        "ai_provider": "ollama",        <- proveedor por defecto (o "none")
        "ai_providers": {
            "ollama": {
                "type": "ollama",
                "host": "http://127.0.0.1:11434",
                "model": "qwen3:4b",
                "auto_start": false
            },
            "lmstudio": {
                "type": "openai_compatible",
                "host": "http://127.0.0.1:1234/v1",
                "model": "local-model"
            }
        }
    }

Se pueden definir tantas entradas como se quiera dentro de
`ai_providers` (una o varias IAs conectadas a la vez); cuál se usa en
cada llamada se elige con `ModelManager.generate(..., provider="lmstudio")`,
o queda fija la marcada en `ai_provider` si no se especifica ninguna.
"""

from __future__ import annotations

from ai.providers.base_provider import BaseProvider
from ai.providers.none_provider import NoneProvider

# type (en config) -> ruta de import perezoso "módulo:Clase".
# Perezoso a propósito: si el usuario no ha configurado un proveedor de
# un tipo concreto, ARUS no debe fallar al arrancar solo porque la
# dependencia de ESE proveedor (p. ej. el paquete `ollama`) no esté
# instalada. Añadir un motor nuevo compatible con OpenAI no necesita
# código nuevo aquí: basta con una entrada de configuración con
# "type": "openai_compatible".
PROVIDER_TYPES = {
    "ollama": ("ai.providers.local_provider", "LocalProvider"),
    "openai_compatible": ("ai.providers.openai_compatible_provider", "OpenAICompatibleProvider"),
}


def build_provider(type_name: str, config: dict) -> BaseProvider:
    """Construye un proveedor concreto a partir de su tipo y configuración."""
    entry = PROVIDER_TYPES.get(type_name)
    if entry is None:
        raise ValueError(
            f"Tipo de proveedor de IA desconocido: '{type_name}'. "
            f"Tipos soportados: {', '.join(PROVIDER_TYPES)}."
        )
    module_name, class_name = entry
    import importlib

    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    kwargs = {k: v for k, v in config.items() if k not in ("type", "auto_start")}
    return cls(**kwargs)


def build_providers_from_settings(settings) -> tuple[dict[str, BaseProvider], str]:
    """Construye todos los proveedores configurados en Settings.

    Devuelve (diccionario {nombre: proveedor}, nombre_del_proveedor_por_defecto).
    Si algún proveedor individual falla al construirse (config incompleta,
    dependencia no instalada, etc.) no se cae toda la aplicación: se omite
    ese proveedor y se sigue con el resto.
    """
    ai_providers_config = settings.get("ai_providers", {}) or {}
    default_name = settings.get("ai_provider", "none")

    providers: dict[str, BaseProvider] = {}
    for name, provider_config in ai_providers_config.items():
        type_name = provider_config.get("type")
        try:
            providers[name] = build_provider(type_name, provider_config)
        except Exception as e:
            print(f"[ARUS] No se pudo conectar el proveedor de IA '{name}': {e}")

    if not providers:
        providers["none"] = NoneProvider()
        default_name = "none"
    elif default_name not in providers:
        # El "ai_provider" por defecto no está entre los que sí se
        # construyeron con éxito: cae de forma segura al primero disponible
        # en vez de reventar.
        default_name = next(iter(providers))

    return providers, default_name


def should_auto_start(settings, provider_name: str | None = None) -> tuple[bool, dict]:
    """Indica si hay que auto-arrancar el proceso de un proveedor local
    (por ejemplo, lanzar `ollama serve`) y con qué configuración.

    Antes, ARUS mataba y relanzaba Ollama sin preguntar en cada arranque,
    aunque el usuario quisiera usar otra IA o ninguna. Ahora solo se
    auto-arranca si el proveedor activo es de tipo "ollama" y su propia
    configuración lo pide explícitamente con "auto_start": true.
    """
    ai_providers_config = settings.get("ai_providers", {}) or {}
    name = provider_name or settings.get("ai_provider", "none")
    provider_config = ai_providers_config.get(name, {})
    return (
        provider_config.get("type") == "ollama" and bool(provider_config.get("auto_start")),
        provider_config,
    )
