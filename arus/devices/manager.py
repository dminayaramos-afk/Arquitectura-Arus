"""
ARUS
Device Manager
Phase 41
"""

from .device import Device
from .repository import DeviceRepository
from .detector import DeviceDetector


class DeviceManager:


    def __init__(self):

        self.devices = {}

        self.repository = DeviceRepository()

        self.detector = DeviceDetector()



    def register(
        self,
        name,
        device_type
    ):

        device = Device(
            name,
            device_type
        )


        detected = self.detector.detect()


        for key,value in detected.items():

            device.capabilities.set_capability(
                key,
                value
            )


        self.devices[name] = device

        self.repository.save(device)

        return device



    def get(
        self,
        name
    ):

        return self.devices.get(name)



    def list(self):

        return list(
            self.devices.values()
        )



    def count(self):

        return len(
            self.devices
        )
