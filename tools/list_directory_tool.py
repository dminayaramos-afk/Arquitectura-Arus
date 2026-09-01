"""
ARUS
List Directory Tool
"""

from pathlib import Path

from tools.base_tool import BaseTool


class ListDirectoryTool(BaseTool):

    name = "list_directory"

    description = "Lista el contenido de un directorio."

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Ruta del directorio"
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

        folder = Path(path)

        if not folder.exists():

            return "ERROR: El directorio no existe."

        if not folder.is_dir():

            return "ERROR: La ruta no es un directorio."

        files = sorted(
            x.name
            for x in folder.iterdir()
        )

        return "\n".join(files)
