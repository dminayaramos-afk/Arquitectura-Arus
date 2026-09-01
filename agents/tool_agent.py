"""
ARUS
Tool Agent
"""

from __future__ import annotations

from datetime import datetime
import base64
import hashlib
import uuid
import json
import platform
import ast
import operator
import json
import uuid
import urllib.parse

from agents.base_agent import BaseAgent
from agents.agent_response import AgentResponse


class ToolAgent(BaseAgent):

    def can_handle(self, request):

        text = request.message.lower()

        tools = (
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
            "sistema"
        )

        return any(x in text for x in tools)

    def execute(self, request):

        text = request.message.strip()

        while text.lower().startswith("arus >"):
            text = text[6:].strip()

        text = " ".join(text.split())

        lower = text.lower()
        # OPERACIONES MATEMATICAS DIRECTAS

        import re

        numeros = re.findall(r"\d+", text)


        if "multiplica" in lower or "multiplicar" in lower:
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(int(numeros[0]) * int(numeros[1]))
                )


        if "suma" in lower:
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(sum(map(int, numeros)))
                )


        if "resta" in lower:
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(int(numeros[0]) - int(numeros[1]))
                )


        if "divide" in lower:
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(int(numeros[0]) / int(numeros[1]))
                )




        if lower in (
            "herramientas",
            "lista herramientas",
            "tools"
        ):
            return AgentResponse(
                True,
                """Herramientas ARUS:

✓ hora
✓ fecha
✓ calc
✓ multiplica
✓ suma
✓ resta
✓ divide
✓ uuid
✓ md5
✓ sha1
✓ sha224
✓ sha256
✓ sha512
✓ blake2b
✓ blake2s
✓ base64
✓ urlencode
✓ urldecode
✓ reverse
✓ length
✓ json
✓ sysinfo"""
            )

        if lower.startswith("sha256 "):
            return AgentResponse(True, hashlib.sha256(text[7:].encode()).hexdigest())

        if lower.startswith("md5 "):
            return AgentResponse(True, hashlib.md5(text[4:].encode()).hexdigest())

        if lower.startswith("sha1 "):
            return AgentResponse(True, hashlib.sha1(text[5:].encode()).hexdigest())

        if lower.startswith("sha224 "):
            return AgentResponse(True, hashlib.sha224(text[7:].encode()).hexdigest())

        if lower.startswith("blake2b "):
            return AgentResponse(True, hashlib.blake2b(text[8:].encode()).hexdigest())

        if lower.startswith("blake2s "):
            return AgentResponse(True, hashlib.blake2s(text[8:].encode()).hexdigest())

        if lower.startswith("base64 "):
            return AgentResponse(
                True,
                base64.b64encode(text[7:].encode()).decode()
            )

        if lower.startswith("urlencode "):
            return AgentResponse(
                True,
                urllib.parse.quote(text[10:])
            )

        if lower.startswith("urldecode "):
            return AgentResponse(
                True,
                urllib.parse.unquote(text[10:])
            )

        if lower.startswith("reverse "):
            return AgentResponse(
                True,
                text[8:][::-1]
            )

        if lower.startswith("length "):
            return AgentResponse(
                True,
                str(len(text[7:]))
            )


        if lower.startswith("uuid"):
            return AgentResponse(
                True,
                str(uuid.uuid4())
            )

        if lower.startswith("json "):
            try:
                obj = json.loads(text[5:])
                return AgentResponse(
                    True,
                    json.dumps(obj, indent=2, ensure_ascii=False)
                )
            except Exception as e:
                return AgentResponse(
                    False,
                    f"JSON inválido: {e}"
                )

        if lower.startswith("sysinfo"):
            return AgentResponse(
                True,
                f"Sistema: {platform.system()} | "
                f"Python: {platform.python_version()} | "
                f"Arquitectura: {platform.machine()}"
            )


        if lower.startswith(("multiplica ", "multiplicar ")):
            import re
            numeros = re.findall(r"[-]?\\d+", text)
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(int(numeros[0]) * int(numeros[1]))
                )


        if lower.startswith(("suma ", "sumar ")):
            import re
            numeros = re.findall(r"[-]?\\d+", text)
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(sum(map(int, numeros)))
                )


        if lower.startswith(("resta ", "restar ")):
            import re
            numeros = re.findall(r"[-]?\\d+", text)
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(int(numeros[0]) - int(numeros[1]))
                )


        if lower.startswith(("divide ", "dividir ")):
            import re
            numeros = re.findall(r"[-]?\\d+", text)
            if len(numeros) >= 2:
                return AgentResponse(
                    True,
                    str(int(numeros[0]) / int(numeros[1]))
                )


        if lower.startswith(("multiplica ", "multiplicar ")):

            import re

            numeros = re.findall(r"\\d+", text)

            if len(numeros) >= 2:

                return AgentResponse(
                    True,
                    str(int(numeros[0]) * int(numeros[1]))
                )


        if lower.startswith(("resta ", "restar ")):

            import re

            numeros = re.findall(r"\\d+", text)

            if len(numeros) >= 2:

                return AgentResponse(
                    True,
                    str(int(numeros[0]) - int(numeros[1]))
                )


        if lower.startswith(("suma ", "sumar ")):

            import re

            numeros = re.findall(r"\\d+", text)

            if len(numeros) >= 2:

                return AgentResponse(
                    True,
                    str(int(numeros[0]) + int(numeros[1]))
                )


        if lower.startswith(("divide ", "dividir ")):

            import re

            numeros = re.findall(r"\\d+", text)

            if len(numeros) >= 2:

                return AgentResponse(
                    True,
                    str(int(numeros[0]) / int(numeros[1]))
                )

        if lower.startswith("calc "):
            try:
                expr = text[5:]

                allowed = {
                    ast.Add: operator.add,
                    ast.Sub: operator.sub,
                    ast.Mult: operator.mul,
                    ast.Div: operator.truediv,
                    ast.Pow: operator.pow
                }

                def calc_node(node):
                    if isinstance(node, ast.Constant):
                        return node.value

                    if isinstance(node, ast.BinOp):
                        return allowed[type(node.op)](
                            calc_node(node.left),
                            calc_node(node.right)
                        )

                    raise ValueError("Operación no permitida")

                resultado = calc_node(
                    ast.parse(expr, mode="eval").body
                )

                return AgentResponse(
                    True,
                    str(resultado)
                )

            except Exception as e:
                return AgentResponse(
                    False,
                    f"Error cálculo: {e}"
                )

        if lower.startswith("hora"):
            return AgentResponse(
                True,
                datetime.now().strftime("%H:%M:%S")
            )

        if lower.startswith("fecha"):
            return AgentResponse(
                True,
                datetime.now().strftime("%d/%m/%Y")
            )

        return AgentResponse(
            False,
            "Herramienta no disponible."
        )



# PATCH FASE PULIDO
def _arus_multiplica(text):
    import re
    numeros = re.findall(r"\d+", text)
    if len(numeros) >= 2:
        return str(int(numeros[0]) * int(numeros[1]))
    return None

    def execute_message(self, message):
        """
        Adaptador de ejecución para Planner/PlanExecutor.
        Mantiene intacta la API existente de execute().
        """

        from agents.agent_request import AgentRequest

        return self.execute(
            AgentRequest(
                message=str(message)
            )
        )

