"""
ARUS
Multimedia Types
"""

from enum import Enum


class MediaType(Enum):

    AUDIO = "audio"

    VIDEO = "video"

    IMAGE = "image"

    DOCUMENT = "document"

    OTHER = "other"



class MediaStatus(Enum):

    CREATED = "created"

    READY = "ready"

    PLAYING = "playing"

    PAUSED = "paused"

    STOPPED = "stopped"
