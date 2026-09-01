"""
ARUS
File Manager
"""

from .file import LaboratoryFile
from .repository import FileRepository


class FileManager:


    def __init__(self):

        self._files = {}

        self.repository = FileRepository()



    def create(
        self,
        name,
        path,
        file_type
    ):

        file = LaboratoryFile(
            name,
            path,
            file_type
        )

        self._files[name] = file

        self.repository.save(file)

        return file



    def get(
        self,
        name
    ):

        return self._files.get(name)



    def delete(
        self,
        name
    ):

        if name in self._files:

            del self._files[name]



    def list(self):

        return list(
            self._files.values()
        )



    def count(self):

        return len(
            self._files
        )
