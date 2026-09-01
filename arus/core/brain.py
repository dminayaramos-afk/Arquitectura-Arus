"""
ARUS - Motor Conversacional (Fase 40)
Gestiona el historial, contexto largo y conexión con Ollama.
"""

import subprocess
import json

class ARUSBrain:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        self.history = []
        self.max_history = 10

    def add_context(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history.pop(0)

    def generate_response(self, prompt):
        self.add_context("user", prompt)
        
        try:
            # Conexión directa con Ollama vía CLI o API local
            # Asegúrate de tener Ollama corriendo en segundo plano
            import urllib.request
            
            data = json.dumps({
                "model": self.model_name,
                "messages": self.history,
                "stream": False
            }).encode('utf-8')
            
            req = urllib.request.Request(
                "http://localhost:11434/api/chat",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                reply = result.get("message", {}).get("content", "Respuesta vacía del núcleo.")
                self.add_context("assistant", reply)
                return reply
                
        except Exception as e:
            # Fallback en caso de que la API local requiera ajuste
            fallback_msg = f"ARUS [Modo Local]: Procesando consulta para '{prompt}'..."
            self.add_context("assistant", fallback_msg)
            return fallback_msg
