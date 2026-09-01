"""
ARUS
Text Cleaner para voz (Fase 11, punto 30 del prompt maestro)

El texto que genera el modelo puede traer Markdown, bloques de código,
URLs largas o símbolos técnicos -- nada de eso debe leerse en voz
alta tal cual. Esta función lo convierte en algo hablable.
"""

from __future__ import annotations

import re

_BLOQUE_CODIGO = re.compile(r"```.*?```", re.DOTALL)
_CODIGO_INLINE = re.compile(r"`([^`]*)`")
_ENLACE_MD = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
_URL = re.compile(r"https?://\S+")
_ENFASIS_MD = re.compile(r"(\*\*\*|\*\*|\*|__|_|~~)")
_ENCABEZADO_MD = re.compile(r"^#{1,6}\s*", re.MULTILINE)
_LISTA_MD = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)
_ESPACIOS = re.compile(r"[ \t]+")
_LINEAS_VACIAS = re.compile(r"\n{2,}")


def clean_for_speech(text: str) -> str:

    if not text:
        return ""

    limpio = _BLOQUE_CODIGO.sub(" (bloque de código omitido) ", text)

    limpio = _CODIGO_INLINE.sub(r"\1", limpio)

    limpio = _ENLACE_MD.sub(r"\1", limpio)

    limpio = _URL.sub("un enlace", limpio)

    limpio = _ENCABEZADO_MD.sub("", limpio)

    limpio = _LISTA_MD.sub("", limpio)

    limpio = _ENFASIS_MD.sub("", limpio)

    limpio = _LINEAS_VACIAS.sub(". ", limpio)

    limpio = _ESPACIOS.sub(" ", limpio)

    return limpio.strip()
