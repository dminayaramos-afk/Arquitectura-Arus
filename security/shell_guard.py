"""
ARUS
Shell Guard
"""

from __future__ import annotations


class ShellGuard:

    def __init__(self):

        self.blocked = [

            "rm ",
            "sudo ",
            "shutdown",
            "reboot",
            "mkfs",
            "dd ",
            "chmod 777",
            "chown",
            "passwd",
            "useradd",
            "userdel",
            "systemctl",
            "service ",
            "kill ",
            "killall",
            ":(){",
            "> /dev/",
            ">/dev/",
            "curl |",
            "wget |",

        ]

        self.allowed_commands = [

            "pwd",
            "ls",
            "cat",
            "echo",
            "find",
            "grep",
            "python3",
            "git",
            "pip",
            "mkdir",
            "touch",
            "cp",
            "mv",
            "head",
            "tail",

        ]


    def allowed(
        self,
        command: str,
    ):

        cmd = command.strip().lower()

        for item in self.blocked:

            if item in cmd:

                return False

        first = cmd.split()[0]

        if first not in self.allowed_commands:

            return False

        return True
