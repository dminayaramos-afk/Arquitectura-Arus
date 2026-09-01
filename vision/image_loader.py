"""
ARUS
Image Loader (Fase 12)

Valida y convierte una imagen a base64 (formato que espera el campo
`images` de ollama.chat para modelos multimodales). Alcance acotado a
formatos de imagen comunes y un límite de tamaño razonable, igual que
document_parser.py (Fase 8) para texto.
"""

from __future__ import annotations

import base64
from pathlib import Path

EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

# Un límite de tamaño razonable para no mandar imágenes enormes a un
# modelo local en un equipo con recursos limitados (punto 89).
LIMITE_BYTES = 8 * 1024 * 1024  # 8 MB


class ImageLoader:

    def puede_leer(self, path: Path) -> bool:

        return path.suffix.lower() in EXTENSIONES_IMAGEN

    def cargar_base64(self, path: str) -> str:

        ruta = Path(path)

        if not ruta.exists():
            raise FileNotFoundError(f"No existe: {path}")

        if not ruta.is_file():
            raise ValueError(f"No es un archivo: {path}")

        if not self.puede_leer(ruta):
            raise ValueError(
                f"Extensión de imagen no soportada: {ruta.suffix} "
                f"(soportadas: {', '.join(sorted(EXTENSIONES_IMAGEN))})"
            )

        if ruta.stat().st_size > LIMITE_BYTES:
            raise ValueError(
                f"Imagen demasiado grande ({ruta.stat().st_size} bytes, "
                f"límite {LIMITE_BYTES})."
            )

        return base64.b64encode(ruta.read_bytes()).decode("ascii")
