"""
ARUS Intent Detector
"""

class IntentDetector:

    def detect(self, message):

        text = message.lower().strip()

        # Herramientas (primero)

        herramientas = (
            "hora",
            "fecha",
            "calc",
            "calcula",
            "calcular",
            "multiplica",
            "multiplicar",
            "suma",
            "sumar",
            "resta",
            "restar",
            "divide",
            "dividir",
            "uuid",
            "md5",
            "sha1",
            "sha224",
            "sha256",
            "sha512",
            "blake2b",
            "blake2s",
            "base64",
            "urlencode",
            "urldecode",
            "hex",
            "reverse",
            "invertir",
            "length",
            "longitud",
            "json",
            "sysinfo",
            "sistema",
            "herramientas",
            "lista herramientas",
            "tools"
        )

        if (
            any(x in text for x in herramientas)
            or any(op in text for op in ("+", "-", "*", "/"))
        ):
            return "tool"

        # Conversación
        if any(x in text for x in (
            "hola",
            "buenas",
            "gracias",
            "adios",
            "adiós",
        )):
            return "chat"

        # Programación
        if any(x in text for x in (
            "python",
            "codigo",
            "código",
            "programa",
            "script",
            "error",
        )):
            return "coding"

        # Preguntas
        if any(x in text for x in (
            "qué",
            "que",
            "cómo",
            "como",
            "explica",
        )):
            return "question"

        return "ai"
