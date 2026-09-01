"""
ARUS
Permission Manager
"""

from __future__ import annotations


class PermissionManager:

    def __init__(self):

        self.rules = {

            "calculator": False,
            "time": False,
            "search": False,
            "web": False,
            "web_reader": False,
            "find_file": False,
            "list_directory": False,
            "project": False,
            "python_check": False,

            "file": True,
            "file_writer": True,
            "replace_text": True,
            "shell": True,
            "github_clone": True,

        }

    def requires_confirmation(
        self,
        tool: str,
    ) -> bool:

        return self.rules.get(
            tool,
            True,
        )
