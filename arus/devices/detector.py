"""
ARUS
Device Capability Detector
Phase 41
"""

import shutil


class DeviceDetector:


    def detect(self):

        capabilities = {

            "screen": True,

            "microphone": self.has_microphone(),

            "speaker": self.has_speaker(),

            "touch": False

        }

        return capabilities



    def has_microphone(self):

        return True



    def has_speaker(self):

        return shutil.which(
            "ffplay"
        ) is not None or True

