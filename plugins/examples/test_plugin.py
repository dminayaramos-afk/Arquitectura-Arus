"""
Plugin de prueba ARUS.
"""

from plugins.plugin import Plugin


class TestPlugin(Plugin):

    name = "test_plugin"

    version = "0.1.0"


    def initialize(self):

        print(
            "Test Plugin iniciado"
        )


    def shutdown(self):

        print(
            "Test Plugin cerrado"
        )
