"""
ARUS
Vision Manager (Fase 12)

Fachada única: IMAGE -> ImageLoader -> VisionProvider -> ANALYSIS.

No se conecta a Brain.think() automáticamente por dos motivos, no
solo uno:
1. Igual que con RAG (Fase 8), decidir CUÁNDO analizar una imagen es
   una decisión de producto que no toca esta fase.
2. A diferencia de RAG, aquí ni siquiera hay por dónde ENTRARÍA una
   imagen: la interfaz (intocable) no tiene ningún control para subir
   o pegar una imagen. Aunque Brain llamara a esto automáticamente,
   hoy no hay manera de que un usuario le pase una imagen a ARUS
   desde la GUI. Se deja documentado, no fingido.
"""

from __future__ import annotations

from vision.image_loader import ImageLoader
from vision.vision_provider import VisionProvider, OllamaVisionProvider

PROMPT_POR_DEFECTO = (
    "Describe esta imagen con detalle. Si es una captura de pantalla, "
    "diagrama o esquema técnico, explica qué muestra y señala "
    "cualquier error visible."
)


class VisionManager:

    def __init__(self, provider: VisionProvider = None, loader: ImageLoader = None):

        self.provider = provider or OllamaVisionProvider()

        self.loader = loader or ImageLoader()

    def is_available(self) -> bool:

        return self.provider.is_available()

    def analyze(self, image_path: str, prompt: str = None) -> str:

        try:
            imagen_base64 = self.loader.cargar_base64(image_path)
        except Exception as e:
            return f"No se pudo leer la imagen: {e}"

        return self.provider.analyze(imagen_base64, prompt or PROMPT_POR_DEFECTO)
