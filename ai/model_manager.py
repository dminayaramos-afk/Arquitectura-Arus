"""
ARUS
Model Manager

ARUS MARK 9, punto 3 (Multi-IA): antes ModelManager solo podía usar
LocalProvider, sin ninguna forma de registrar o elegir otro proveedor
sin reescribir esta clase. Se prepara la arquitectura para varios
proveedores/modelos (BaseProvider ya existía, pero nada lo aprovechaba
para esto) SIN implementar servicios externos que no existen en el
proyecto (no hay claves de OpenAI/Anthropic configuradas -- se deja
listo, no se inventa un proveedor que no se puede probar de verdad).

Retrocompatible: `ModelManager().generate(message, history)` sigue
funcionando exactamente igual que antes (usa "local" por defecto).
"""

from __future__ import annotations

from typing import Optional

from ai.providers.base_provider import BaseProvider


class ModelManager:

    def __init__(self, providers: Optional[dict[str, BaseProvider]] = None, default: Optional[str] = None):

        if providers is None:
            # Sin proveedores explícitos: se construyen desde la
            # configuración del usuario (config/settings.json), en vez de
            # asumir Ollama por defecto como antes. Si el usuario no ha
            # conectado ninguna IA todavía, se usa un proveedor "none"
            # honesto que lo explica, en vez de fallar en silencio.
            from ai.provider_factory import build_providers_from_settings
            from config.settings import Settings

            settings = Settings()
            settings.load()
            providers, resolved_default = build_providers_from_settings(settings)
            default = default or resolved_default

        self.providers = providers

        self.default = default or next(iter(self.providers), "none")

    def register_provider(self, name: str, provider: BaseProvider):
        """Añade un proveedor sin tener que tocar esta clase ni Brain/Controller."""

        self.providers[name] = provider

    def available_providers(self) -> list[str]:

        return list(self.providers.keys())

    def generate(
        self,
        message: str,
        history=None,
        provider: Optional[str] = None,
    ) -> str:

        nombre = provider or self.default

        proveedor = self.providers.get(nombre)

        if proveedor is None:
            raise ValueError(
                f"Proveedor de IA no registrado: '{nombre}'. "
                f"Disponibles: {', '.join(self.available_providers())}"
            )

        return proveedor.generate(
            message,
            history,
        )
