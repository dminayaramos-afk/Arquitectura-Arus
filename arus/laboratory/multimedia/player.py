"""
ARUS
Multimedia Player
"""

from .types import MediaStatus


class MultimediaPlayer:


    def __init__(self):

        self.current = None


    def load(self, media):

        self.current = media

        media.status = MediaStatus.READY


    def play(self):

        if self.current:

            self.current.status = MediaStatus.PLAYING


    def pause(self):

        if self.current:

            self.current.status = MediaStatus.PAUSED


    def stop(self):

        if self.current:

            self.current.status = MediaStatus.STOPPED


    def info(self):

        if not self.current:
            return None

        return self.current.info()
