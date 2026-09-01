"""
ARUS
Virtual Laboratory
Workspace Manager
"""

from __future__ import annotations

from arus.laboratory.models.workspace import Workspace
from arus.laboratory.exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceNotFoundError,
)


class WorkspaceManager:

    def __init__(self):

        self._workspaces = {}

    def create(self, name: str, description: str = "") -> Workspace:

        if name in self._workspaces:
            raise WorkspaceAlreadyExistsError(
                f"El Workspace '{name}' ya existe."
            )

        workspace = Workspace(
            name=name,
            description=description,
        )

        self._workspaces[name] = workspace

        return workspace

    def get(self, name: str) -> Workspace:

        workspace = self._workspaces.get(name)

        if workspace is None:
            raise WorkspaceNotFoundError(
                f"No existe el Workspace '{name}'."
            )

        return workspace

    def exists(self, name: str) -> bool:

        return name in self._workspaces

    def delete(self, name: str):

        if name not in self._workspaces:
            raise WorkspaceNotFoundError(
                f"No existe el Workspace '{name}'."
            )

        del self._workspaces[name]

    def list(self):

        return list(self._workspaces.values())

    def count(self):

        return len(self._workspaces)

    def clear(self):

        self._workspaces.clear()
