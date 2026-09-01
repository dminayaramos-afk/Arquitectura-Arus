"""
ARUS Command Manager
"""

from commands.command_registry import CommandRegistry
from commands.builtins.help_command import HelpCommand
from commands.status_command import StatusCommand
from diagnostics.system_check import SystemCheck


class CommandManager:


    def __init__(
        self,
        brain=None,
        skills=None,
    ):

        self.registry = CommandRegistry()

        self.diagnostics = SystemCheck(
            brain=brain,
            skills=skills,
            commands=self,
        )

        self.load_commands()



    def load_commands(self):

        self.registry.register(
            HelpCommand(
                self.registry
            )
        )


        self.registry.register(
            StatusCommand(
                self.diagnostics
            )
        )



    def execute(
        self,
        text,
    ):

        if not text.startswith("/"):
            return None


        parts = text[1:].split()

        name = parts[0]

        args = parts[1:]


        command = self.registry.get(
            name
        )


        if command is None:

            return "Comando desconocido"


        return command.execute(
            args
        )
