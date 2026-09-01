"""
ARUS
Device Types
"""

from enum import Enum


class DeviceType(Enum):

    CPU="cpu"

    GPU="gpu"

    SENSOR="sensor"

    CAMERA="camera"

    STORAGE="storage"

    NETWORK="network"

    OTHER="other"



class DeviceStatus(Enum):

    CREATED="created"

    ONLINE="online"

    OFFLINE="offline"

    ERROR="error"
