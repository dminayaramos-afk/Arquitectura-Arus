"""
ARUS
Device Discovery
"""

import platform
import os

from .types import DeviceType


class DeviceDiscovery:


    def scan(self):

        devices = []

        devices.append({
            "name": platform.processor() or "CPU",
            "type": DeviceType.CPU
        })

        devices.append({
            "name": platform.system(),
            "type": DeviceType.OTHER
        })

        if os.path.exists("/dev"):
            devices.append({
                "name": "/dev",
                "type": DeviceType.STORAGE
            })

        return devices
