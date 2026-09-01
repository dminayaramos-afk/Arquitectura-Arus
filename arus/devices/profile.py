"""
ARUS
Device Profile
Phase 42
"""


from .types import DeviceType
from .device import Device
from .detector import DeviceDetector



class DeviceProfile:


    def __init__(self):

        self.detector = DeviceDetector()



    def create(self):

        device = Device(
            "local_machine",
            DeviceType.OTHER
        )


        capabilities = self.detector.detect()


        for key, value in capabilities.items():

            device.capabilities.set_capability(
                key,
                value
            )


        device.connect()


        return device
