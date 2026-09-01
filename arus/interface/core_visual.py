import math
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QBrush
from PySide6.QtWidgets import QWidget


class NeuralCore(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle"  # idle, listening, learning, speaking, investigating
        self.angle = 0
        self.pulse = 0
        self.nodes_offset = 0

        # Timer para actualizar las animaciones fluidas en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)  # ~33 FPS para fluidez total

    def set_state(self, state):
        # Mapeo de estados externos a los modos visuales de la hoja de ruta
        states_map = {
            "idle": "idle",
            "listening": "listening",
            "learning": "learning",
            "speaking": "speaking",
            "thinking": "thinking",
            "investigating": "investigating"
        }
        self.state = states_map.get(state, "idle")
        self.update()

    def update_animation(self):
        self.angle = (self.angle + 2) % 360
        self.pulse = (self.pulse + 1) % 100
        self.nodes_offset += 0.5
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(center_x, center_y) - 40

        # Color base cian HUD
        cyan_color = QColor(0, 229, 255)
        dark_cyan = QColor(0, 77, 115)

        # -------------------------------------------------------------------------
        # 1. FONDO Y ANILLOS EXTERIORES HUD
        # -------------------------------------------------------------------------
        painter.setPen(QPen(dark_cyan, 1, Qt.DashLine))
        painter.drawEllipse(int(center_x - radius), int(center_y - radius), int(radius * 2), int(radius * 2))

        painter.setPen(QPen(cyan_color, 1.5))
        painter.drawEllipse(int(center_x - radius * 0.7), int(center_y - radius * 0.7), int(radius * 1.4), int(radius * 1.4))

        # Anillo central dinámico según estado
        if self.state == "investigating":
            # Toda la red se activa con anillos concéntricos múltiples
            painter.setPen(QPen(cyan_color, 2, Qt.DotLine))
            pulse_r = (radius * 0.5) + (self.pulse % 20)
            painter.drawEllipse(int(center_x - pulse_r), int(center_y - pulse_r), int(pulse_r * 2), int(pulse_r * 2))
        
        inner_ring_r = radius * 0.4
        if self.state == "thinking":
            inner_ring_r += math.sin(math.radians(self.angle * 4)) * 6
        elif self.state == "speaking":
            inner_ring_r += math.cos(math.radians(self.angle * 6)) * 10

        painter.setPen(QPen(cyan_color, 2))
        painter.drawEllipse(int(center_x - inner_ring_r), int(center_y - inner_ring_r), int(inner_ring_r * 2), int(inner_ring_r * 2))

        # -------------------------------------------------------------------------
        # 2. CONEXIONES NEURONALES (Rayos y Nodos)
        # -------------------------------------------------------------------------
        num_nodes = 24 if self.state != "investigating" else 40
        for i in range(num_nodes):
            angle_deg = i * (360 / num_nodes) + (self.angle if self.state == "learning" else 0)
            angle_rad = math.radians(angle_deg)

            # Distancia de los nodos según el estado
            var_dist = radius
            if self.state == "listening":
                var_dist += math.sin(math.radians(self.angle * 3 + i * 15)) * 15
            elif self.state == "speaking":
                var_dist += math.cos(math.radians(self.angle * 5 + i * 10)) * 20
            elif self.state == "investigating":
                var_dist += math.sin(math.radians(self.angle * 2 + i * 30)) * 25

            node_x = center_x + math.cos(angle_rad) * var_dist
            node_y = center_y + math.sin(angle_rad) * var_dist

            # Líneas desde el centro al nodo
            line_pen = QPen(cyan_color, 1 if self.state != "investigating" else 1.5)
            if self.state == "idle":
                line_pen.setStyle(Qt.DotLine)
            painter.setPen(line_pen)
            painter.drawLine(int(center_x), int(center_y), int(node_x), int(node_y))

            # Dibujar nodo exterior
            painter.setBrush(QBrush(QColor(1, 8, 20)))
            painter.drawEllipse(int(node_x - 3), int(node_y - 3), 6, 6)

        # -------------------------------------------------------------------------
        # 3. NÚCLEO CENTRAL PULSANTE
        # -------------------------------------------------------------------------
        core_size = 12
        if self.state == "listening":
            core_size += (self.pulse % 10)
        elif self.state == "learning":
            core_size += (self.angle % 8)
        elif self.state == "speaking":
            core_size += math.sin(math.radians(self.angle * 8)) * 6

        painter.setBrush(QBrush(cyan_color))
        painter.setPen(QPen(Qt.white, 1))
        painter.drawEllipse(int(center_x - core_size / 2), int(center_y - core_size / 2), int(core_size), int(core_size))
