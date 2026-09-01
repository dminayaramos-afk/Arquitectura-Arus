"""
ARUS
Project Tool
"""

from pathlib import Path

from tools.base_tool import BaseTool


class ProjectTool(BaseTool):

    name = "project"

    description = "Crea la estructura básica de un proyecto."

    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Ruta del proyecto"
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

        root = Path(path)

        folders = [
            "src",
            "tests",
            "docs",
            "data",
        ]

        for folder in folders:

            (root / folder).mkdir(
                parents=True,
                exist_ok=True,
            )

        (root / "README.md").write_text(
            "# Nuevo Proyecto\n",
            encoding="utf-8",
        )

        return f"Proyecto creado en {root}"
