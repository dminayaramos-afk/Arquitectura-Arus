"""
ARUS Status Command
"""

from commands.command import Command


class StatusCommand(Command):


    name = "status"


    def __init__(
        self,
        diagnostics
    ):

        self.diagnostics = diagnostics



    def execute(
        self,
        args=None
    ):

        return self.diagnostics.check()
