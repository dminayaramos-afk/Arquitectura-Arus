"""
ARUS
Adaptive Interface
Phase 42
"""


class AdaptiveInterface:


    def select(
        self,
        capabilities
    ):

        mode = capabilities.interface_mode()


        if mode == "full":

            return "chat_voice_animation"


        if mode == "chat":

            return "chat_only"


        if mode == "voice":

            return "voice_only"


        return "basic"
