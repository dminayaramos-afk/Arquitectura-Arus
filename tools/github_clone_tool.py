"""
ARUS
GitHub Clone Tool
"""

import subprocess
from tools.base_tool import BaseTool

class GithubCloneTool(BaseTool):
    name = "github_clone"
    description = "Clona repositorios de GitHub."
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL del repositorio de GitHub"},
            "destination": {"type": "string", "description": "Carpeta de destino"}
        },
        "required": ["url", "destination"]
    }

    def execute(self, url: str, destination: str):
        try:
            result = subprocess.run(["git", "clone", url, destination], capture_output=True, text=True)
            if result.returncode == 0:
                return "Repositorio clonado con éxito."
            else:
                return f"ERROR: {result.stderr}"
        except Exception as e:
            return f"ERROR: {str(e)}"
