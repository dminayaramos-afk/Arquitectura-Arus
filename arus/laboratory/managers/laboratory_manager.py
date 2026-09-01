from __future__ import annotations

from arus.laboratory.repositories import SQLiteLaboratoryRepository
from arus.laboratory.managers.runtime_manager import RuntimeManager
"""
ARUS
Virtual Laboratory
Laboratory Manager
"""



from typing import Dict, List, Optional

from arus.laboratory.models.laboratory import Laboratory
from arus.laboratory.models.status import LaboratoryStatus
from arus.laboratory.models.workspace import Workspace

from arus.laboratory.exceptions import (
    LaboratoryAlreadyExistsError,
    LaboratoryNotFoundError,
)


class LaboratoryManager:
    """
    Gestiona todos los laboratorios de ARUS.
    """


    def __init__(self):

        self._laboratories = {}

        self.repository = SQLiteLaboratoryRepository()

        self.runtime_manager = RuntimeManager()


    def create(
        self,
        name: str,
        description: str = "",
        owner: Optional[str] = None,
    ) -> Laboratory:

        if name in self._laboratories:
            raise LaboratoryAlreadyExistsError(
                f"Ya existe un laboratorio llamado '{name}'."
            )

        laboratory = Laboratory(
            name=name,
            description=description,
            owner=owner,
        )

        laboratory.initialize()
        laboratory.ready()

        self._laboratories[name] = laboratory

        self.repository.save(laboratory)

        return laboratory

    def get(self, name: str) -> Laboratory:

        laboratory = self._laboratories.get(name)

        if laboratory is None:
            raise LaboratoryNotFoundError(
                f"No existe el laboratorio '{name}'."
            )

        return laboratory

    def exists(self, name: str) -> bool:

        return name in self._laboratories

    def remove(self, name: str):

        if name not in self._laboratories:
            raise LaboratoryNotFoundError(
                f"No existe el laboratorio '{name}'."
            )

        self._laboratories[name].delete()

        del self._laboratories[name]

        self.repository.delete(name)

    def list(self) -> List[Laboratory]:

        return list(self._laboratories.values())

    def start(self, name: str):

        self.get(name).start()

    def pause(self, name: str):

        self.get(name).pause()

    def finish(self, name: str):

        self.get(name).finish()

    def archive(self, name: str):

        self.get(name).archive()

    def status(self, name: str) -> LaboratoryStatus:

        return self.get(name).status

    def info(self, name: str):

        return self.get(name).info()

    def count(self):

        return len(self._laboratories)



    def create_workspace(
        self,
        laboratory_name: str,
        workspace_name: str,
        description: str = "",
    ) -> Workspace:

        laboratory = self.get(laboratory_name)

        if laboratory.workspace_exists(workspace_name):
            raise ValueError(
                f"Ya existe el Workspace '{workspace_name}'."
            )

        workspace = Workspace(
            name=workspace_name,
            description=description,
        )

        laboratory.add_workspace(workspace)

        return workspace

    def get_workspace(
        self,
        laboratory_name: str,
        workspace_name: str,
    ) -> Workspace:

        laboratory = self.get(laboratory_name)

        workspace = laboratory.get_workspace(workspace_name)

        if workspace is None:
            raise ValueError(
                f"No existe el Workspace '{workspace_name}'."
            )

        return workspace

    def remove_workspace(
        self,
        laboratory_name: str,
        workspace_name: str,
    ):

        laboratory = self.get(laboratory_name)

        laboratory.remove_workspace(workspace_name)

    def list_workspaces(
        self,
        laboratory_name: str,
    ):

        laboratory = self.get(laboratory_name)

        return list(laboratory.workspaces.values())






    def load(self, name: str):

        laboratory = self.repository.load(
            name,
            Laboratory,
        )

        if laboratory is None:
            return None

        self._laboratories[name] = laboratory

        return laboratory


    def delete(self, name: str):

        laboratory = self.get(name)

        del self._laboratories[name]

        self.repository.delete(name)

        return laboratory




    def start_runtime(
        self,
        name: str,
    ):

        laboratory = self.get(name)

        return self.runtime_manager.start(
            laboratory
        )


    def get_runtime(
        self,
        name: str,
    ):

        return self.runtime_manager.get(
            name
        )


    def stop_runtime(
        self,
        name: str,
    ):

        return self.runtime_manager.stop(
            name
        )


    def clear(self):

        self._laboratories.clear()
