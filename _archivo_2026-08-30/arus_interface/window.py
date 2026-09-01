"""
ARUS
JARVIS Main Window
"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel
)

from .core_visual import NeuralCore


class ARUSWindow(QMainWindow):


    def __init__(self):

        super().__init__()


        self.setWindowTitle(
            "ARUS AI CORE"
        )


        self.resize(
            900,
            700
        )


        container=QWidget()


        layout=QVBoxLayout()


        self.status=QLabel(
            "ARUS ONLINE"
        )


        self.core=NeuralCore()


        layout.addWidget(
            self.status
        )


        layout.addWidget(
            self.core
        )


        container.setLayout(
            layout
        )


        self.setCentralWidget(
            container
        )
