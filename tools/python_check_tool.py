"""
ARUS
Python Check Tool
"""

from __future__ import annotations

import subprocess

from tools.base_tool import BaseTool


class PythonCheckTool(BaseTool):

    name = "python_check"

    description = "Comprueba si un archivo Python contiene errores."

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Archivo Python"
            }
        },
        "required": [
            "path"
        ]
    }


    def execute(
        self,
        path: str,
    ):

        result = subprocess.run(
            [
                "python3",
                "-m",
                "py_compile",
                path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:

            return "OK"

        return result.stderr
