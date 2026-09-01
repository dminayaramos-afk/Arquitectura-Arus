
"""
ARUS
Multimedia Manager
"""


from arus.laboratory.multimedia import Media
from .repository import MultimediaRepository



class MultimediaManager:


    def __init__(self):

        self._media = {}

        self.repository = MultimediaRepository()



    def add(
        self,
        name,
        path,
        media_type
    ):

        media = Media(
            name,
            path,
            media_type
        )


        self._media[name] = media

        self.repository.save(media)


        return media



    def get(
        self,
        name
    ):

        return self._media.get(
            name
        )



    def delete(
        self,
        name
    ):

        if name in self._media:

            del self._media[name]



    def list(self):

        return list(
            self._media.values()
        )


    def count(self):

        return len(
            self._media
        )
