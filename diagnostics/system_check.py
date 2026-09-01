"""
ARUS
System Check
"""


class SystemCheck:

    def __init__(
        self,
        brain=None,
        skills=None,
        commands=None,
    ):
        self.brain = brain
        self.skills = skills
        self.commands = commands


    def check(self):

        result = {}

        result["brain"] = (
            "OK"
            if self.brain
            else "NO DISPONIBLE"
        )

        result["skills"] = (
            len(list(self.skills.registry.all()))
            if self.skills
            else 0
        )

        result["commands"] = (
            len(list(self.commands.registry.all()))
            if self.commands
            else 0
        )

        result["database"] = "OK"

        result["memory"] = (
            "OK"
            if self.brain and hasattr(self.brain, "memory")
            else "NO DISPONIBLE"
        )

        return result
