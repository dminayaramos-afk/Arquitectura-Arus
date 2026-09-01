import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from agents.tool_agent import ToolAgent
from types import SimpleNamespace


agent = ToolAgent()


tests = [
    "sha224 hola",
    "sha256 hola",
    "md5 hola",
    "sha1 hola",
    "blake2b hola",
    "blake2s hola",
    "base64 hola",
    "reverse ARUS",
    "length inteligencia",
    "urlencode hola mundo",
    "urldecode hola%20mundo",
    "hora",
    "fecha"
]


for cmd in tests:
    req = SimpleNamespace(message=cmd)
    r = agent.execute(req)

    print(
        "[OK]",
        cmd,
        "=>",
        r.answer
    )


print("="*50)
print("FASE 11 TOOLAGENT COMPLETADA")
print("="*50)
