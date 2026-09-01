"""
ARUS
Chat Identity & Chat Interface
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton
)


class ChatWidget(QWidget):

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller

        layout = QVBoxLayout()

        self.history = QTextEdit()
        self.history.setReadOnly(True)

        self.input = QLineEdit()
        self.input.setFocus()
        self.input.returnPressed.connect(self.send)

        self.button = QPushButton("Enviar")
        self.button.clicked.connect(self.send)

        layout.addWidget(self.history)
        layout.addWidget(self.input)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.setStyleSheet("""
        QWidget{
            background:#020611;
            color:#00E5FF;
        }
        QTextEdit{
            background:#010817;
            color:#00E5FF;
            border:1px solid #0077AA;
        }
        QLineEdit{
            background:#010817;
            color:#00FFFF;
            border:1px solid #0077AA;
        }
        QPushButton{
            background:#02172F;
            color:#00E5FF;
        }
        """)

    def add_message(self, text):
        self.history.append(text)

    def send(self):
        text = self.input.text().strip()
        if text:
            self.history.append("Usuario: " + text)

            # Fase 4: ya no se habla directamente con Ollama desde aquí.
            # Se usa el controller que main_window.py ya inyecta
            # (ChatWidget -> ARUSController -> Brain -> ModelManager),
            # para que comandos, skills y el cerebro completo de ARUS
            # participen en la respuesta, no solo el modelo desnudo.
            if self.controller is not None:
                try:
                    response = self.controller.process(text)
                except Exception as e:
                    response = f"Error en el cerebro de ARUS: {e}"
            else:
                response = "ARUS no está conectado a su cerebro (controller no disponible)."

            if not response:
                response = "No se pudo procesar la respuesta del modelo local."
                
            self.history.append("ARUS: " + str(response).strip())
            self.input.clear()
