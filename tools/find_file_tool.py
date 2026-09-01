"""
ARUS
Find File Tool
"""

import os
from tools.base_tool import BaseTool

class FindFileTool(BaseTool):
    name = "find_file"
    description = "Busca archivos en el sistema."
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Patrón de búsqueda del archivo"},
            "path": {"type": "string", "description": "Ruta base de búsqueda"}
        },
        "required": ["pattern", "path"]
    }

    def execute(self, pattern: str, path: str):
        try:
            results = []
            for root, dirs, files in os.walk(path):
                for file in files:
                    if pattern in file:
                        results.append(os.path.join(root, file))
            return "\n".join(results) if results else "No se encontraron archivos."
        except Exception as e:
            return f"ERROR: {str(e)}"
