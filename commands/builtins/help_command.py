"""
ARUS
Help Command
"""

from commands.command import Command


class HelpCommand(Command):


    name = "help"


    def __init__(
        self,
        registry,
    ):

        self.registry = registry



    def execute(
        self,
        args,
    ):

        result = [
            "Comandos disponibles:"
        ]


        for command in self.registry.all():

            result.append(
                f"/{command.name}"
            )


        return "\n".join(result)
