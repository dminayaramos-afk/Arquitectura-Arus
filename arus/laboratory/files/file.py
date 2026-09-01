"""
ARUS
Laboratory File
"""

import uuid
import hashlib
from datetime import datetime

from .types import FileType


class LaboratoryFile:


    def __init__(
        self,
        name,
        path,
        file_type=FileType.OTHER
    ):

        self.id = str(uuid.uuid4())

        self.name = name

        self.path = path

        self.type = file_type

        self.created_at = datetime.now()

        self.size = 0

        self.hash = self.generate_hash()

        self.metadata = {}



    def generate_hash(self):

        return hashlib.sha256(
            self.name.encode()
        ).hexdigest()



    def add_metadata(
        self,
        key,
        value
    ):

        self.metadata[key] = value



    def info(self):

        return {

            "id": self.id,

            "name": self.name,

            "path": self.path,

            "type": self.type.value,

            "size": self.size,

            "hash": self.hash,

            "metadata": self.metadata

        }
