
"""
ARUS
Media Object
"""

import uuid
from datetime import datetime

from .types import MediaType, MediaStatus


class Media:


    def __init__(
        self,
        name,
        path,
        media_type=MediaType.OTHER
    ):

        self.id = str(uuid.uuid4())

        self.name = name

        self.path = path

        self.type = media_type

        self.status = MediaStatus.CREATED

        self.created_at = datetime.now()

        self.metadata = {}



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

            "status": self.status.value,

            "metadata": self.metadata

        }
