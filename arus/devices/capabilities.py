"""
ARUS
Device Capabilities
Phase 41
"""


class DeviceCapabilities:


    def __init__(self):

        self.screen = False

        self.microphone = False

        self.speaker = False

        self.touch = False



    def set_capability(
        self,
        name,
        value
    ):

        if hasattr(
            self,
            name
        ):

            setattr(
                self,
                name,
                value
            )



    def interface_mode(self):

        if self.screen and self.microphone and self.speaker:

            return "full"



        if self.screen and not self.microphone:

            return "chat"



        if self.speaker and not self.screen:

            return "voice"



        return "basic"



    def info(self):

        return {

            "screen": self.screen,

            "microphone": self.microphone,

            "speaker": self.speaker,

            "touch": self.touch,

            "interface": self.interface_mode()

        }
