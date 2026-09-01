"""
File Agent
"""

from brain.agent import Agent


class FileAgent(Agent):

    def __init__(self):

        super().__init__(
            name="FileManager",
            role="filesystem",
            description="Especialista en gestión de archivos.",
            capabilities=[
                "file",
                "file_writer",
                "replace_text",
                "find_file",
                "list_directory",
            ],
        )
