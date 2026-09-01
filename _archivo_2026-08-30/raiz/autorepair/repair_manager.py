"""
ARUS
Repair Manager
"""

from tools.tool_manager import ToolManager


class RepairManager:

    def __init__(self):

        self.tools = ToolManager()


    def check(
        self,
        path: str,
    ):

        return self.tools.execute(
            "python_check",
            path=path,
        )


    def repair(
        self,
        path: str,
    ):

        result = self.check(path)

        if result == "OK":

            return "El archivo no necesita reparación."

        return (
            "Se detectaron errores:\n\n"
            + result
        )
