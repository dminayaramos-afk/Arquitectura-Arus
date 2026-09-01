"""
ARUS
Device Object
Phase 41
"""

import uuid

from .types import DeviceType, DeviceStatus
from .capabilities import DeviceCapabilities


class Device:


    def __init__(
        self,
        name,
        device_type=DeviceType.OTHER
    ):

        self.id = str(uuid.uuid4())

        self.name = name

        self.type = device_type

        self.status = DeviceStatus.CREATED

        self.metadata = {}

        self.capabilities = DeviceCapabilities()



    def connect(self):

        self.status = DeviceStatus.ONLINE



    def disconnect(self):

        self.status = DeviceStatus.OFFLINE



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

            "type": self.type.value,

            "status": self.status.value,

            "metadata": self.metadata,

            "capabilities": self.capabilities.info()

        }
