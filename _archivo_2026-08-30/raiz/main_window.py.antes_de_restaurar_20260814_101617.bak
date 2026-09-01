import requests
import subprocess
import os
import time
from datetime import datetime
import psutil

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QProgressBar, QApplication, QSplitter
)

# Importamos el buscador web para datos en tiempo real
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

from arus.interface.core_visual import NeuralCore
from arus.interface.chat import ChatWidget
from arus.interface.controller import ARUSController
from arus.interface.adaptive import AdaptiveInterface
from arus.devices.profile import DeviceProfile
from arus.core.voice import VoiceCore


class ARUSWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ollama_process = None
        self.iniciar_ollama_automatico()

        self.voice = VoiceCore()
        self.adaptive = AdaptiveInterface()
        self.device_profile = DeviceProfile()
        self.device = self.device_profile.create()
        self.interface_mode = self.adaptive.select(self.device.capabilities)

        self.setWindowTitle("ARUS")
        self.resize(1450, 950)
        self.setMinimumSize(1000, 650)

        # Controladores de red y disco en tiempo real
        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = time.time()
        
        self._last_disk_io = psutil.disk_io_counters()
        self._last_disk_time = time.time()

        estilo_hud = """
            QMainWindow, QWidget {
                background-color: #010814;
                color: #00E5FF;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QFrame {
                background-color: #020B18;
                border: 1px solid #004D73;
                border-radius: 10px;
            }
            QLabel {
                background-color: transparent;
                color: #00E5FF;
            }
            QProgressBar {
                background-color: #01040a;
                color: #FFFFFF;
                border: 1px solid #004D73;
                border-radius: 5px;
                text-align: center;
                height: 12px;
                font-size: 10px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0083B0, stop:1 #00E5FF);
                border-radius: 4px;
            }
            QPushButton {
                background-color: #020B18;
                color: #00E5FF;
                border: 1px solid #004D73;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004D73;
                border-color: #00E5FF;
                color: #FFFFFF;
            }
            QSplitter::handle {
                background-color: #004D73;
                border-radius: 3px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background-color: #00E5FF;
            }
        """
        self.setStyleSheet(estilo_hud)
        if QApplication.instance():
            QApplication.instance().setStyleSheet(estilo_hud)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        self.central.setLayout(self.main_layout)

        # Barra Superior
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(55)
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(20, 0, 20, 0)
        self.top_bar.setLayout(self.top_layout)

        self.lbl_sub_status = QLabel("CORE ONLINE + WEB SEARCH")
        self.lbl_sub_status.setStyleSheet("font-size: 11px; color: #004D73; border: none;")

        self.lbl_title = QLabel("◈   A R U S   ◈")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00E5FF; letter-spacing: 4px; border: none;")

        self.lbl_clock = QLabel("--:--:--")
        self.lbl_clock.setStyleSheet("font-family: monospace; font-size: 13px; border: none;")
        self.clock = self.lbl_clock

        self.top_layout.addWidget(self.lbl_sub_status)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.lbl_title)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.lbl_clock)
        self.main_layout.addWidget(self.top_bar)

        # Cuerpo Central
        self.body_widget = QWidget()
        self.body_layout = QHBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(15)
        self.body_widget.setLayout(self.body_layout)
        self.main_layout.addWidget(self.body_widget, 1)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.body_layout.addWidget(self.main_splitter)

        # Núcleo Neural
        self.core = NeuralCore()
        self.core.setMinimumSize(400, 400)
        self.main_splitter.addWidget(self.core)

        # Panel Derecho
        self.right_panel = QFrame()
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(12, 12, 12, 12)
        self.right_layout.setSpacing(12)
        self.right_panel.setLayout(self.right_layout)

        self.chat_splitter = QSplitter(Qt.Vertical)
        self.right_layout.addWidget(self.chat_splitter)

        self.controller = ARUSController(self.core)
        self.chat = ChatWidget(self.controller)
        self.chat_splitter.addWidget(self.chat)

        # Contenedor de Sistema (CPU, RAM, Disco, Red y Botones)
        self.sys_container = QWidget()
        self.sys_layout = QVBoxLayout()
        self.sys_layout.setContentsMargins(0, 0, 0, 0)
        self.sys_layout.setSpacing(6)
        self.sys_container.setLayout(self.sys_layout)

        self.cpu_label = QLabel("⚡ CPU: 0%")
        self.cpu_label.setStyleSheet("font-weight: bold; color: #00E5FF; border: none;")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)

        self.ram_label = QLabel("💾 RAM: 0%")
        self.ram_label.setStyleSheet("font-weight: bold; color: #00E5FF; border: none;")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)

        self.disk_label = QLabel("💽 DISCO (SSD): 0 KB/s")
        self.disk_label.setStyleSheet("font-weight: bold; color: #00E5FF; border: none;")
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)

        self.info_frame_layout = QHBoxLayout()
        self.temp_label = QLabel("🌡 TEMP: --°C")
        self.temp_label.setStyleSheet("font-weight: bold; color: #00E5FF; border: none;")
        
        self.net_label = QLabel("🌐 RED: ↓ 0 KB/s")
        self.net_label.setStyleSheet("font-weight: bold; color: #00E5FF; border: none; font-size: 11px;")
        
        self.sys_layout.addWidget(self.cpu_label)
        self.sys_layout.addWidget(self.cpu_bar)
        self.sys_layout.addWidget(self.ram_label)
        self.sys_layout.addWidget(self.ram_bar)
        self.sys_layout.addWidget(self.disk_label)
        self.sys_layout.addWidget(self.disk_bar)

        self.info_frame_layout.addWidget(self.temp_label)
        self.info_frame_layout.addStretch()
        self.info_frame_layout.addWidget(self.net_label)
        self.sys_layout.addLayout(self.info_frame_layout)

        # Botones de Acción
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(8)

        self.btn_listen = QPushButton("🎤 Escuchar")
        self.btn_think = QPushButton("🧠 Pensar")
        self.btn_speak = QPushButton("🗣 Hablar")

        self.btn_layout.addWidget(self.btn_listen)
        self.btn_layout.addWidget(self.btn_think)
        self.btn_layout.addWidget(self.btn_speak)

        self.sys_layout.addLayout(self.btn_layout)
        self.chat_splitter.addWidget(self.sys_container)
        
        self.main_splitter.setSizes([850, 450])
        self.chat_splitter.setSizes([430, 250])
        self.main_splitter.addWidget(self.right_panel)

        self.btn_listen.clicked.connect(self.toggle_voice)
        self.btn_think.clicked.connect(self.open_learning)
        self.btn_speak.clicked.connect(self.open_memory)

        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system)
        self.system_timer.start(1000)

        self.core.set_state("idle")
        self.chat.add_message("ARUS: Conectado a la red. Búsqueda web automática habilitada (2026).")

    def buscar_en_web(self, query):
        """Busca información en internet de forma automática para dar respuestas precisas"""
        if not DDGS:
            return ""
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    results.append(r.get('body', ''))
            return "\n".join(results)
        except Exception:
            return ""

    def procesar_con_ia(self, prompt_usuario):
        try:
            query_busqueda = prompt_usuario
            p_lower = prompt_usuario.lower()
            if "presidente" in p_lower or "peru" in p_lower or "chile" in p_lower:
                query_busqueda = "presidente actual de Peru y de Chile 2026"

            contexto_web = self.buscar_en_web(query_busqueda)
            
            prompt_sistema = (
                "Eres ARUS, un sistema inteligente con datos de geografía y política actualizados al 2026. "
                "Chile y Perú son países de Sudamérica limítrofes. "
                "Usa estrictamente la información de internet provista para nombrar correctamente "
                "a los presidentes actuales de Perú y Chile sin inventar datos geográficos ni políticos."
            )
            
            prompt_completo = f"{prompt_sistema}\n\nDatos de internet:\n{contexto_web}\n\nPregunta: {prompt_usuario}\nRespuesta:"

            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'qwen2.5:3b', 
                    'prompt': prompt_completo, 
                    'stream': False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get('response', 'Sin respuesta.').strip()
        except Exception as e:
            pass
        return 'Error de conexión con el modelo.'

    def iniciar_ollama_automatico(self):
        try:
            res = requests.get('http://localhost:11434/', timeout=1)
            if res.status_code == 200:
                return
        except Exception:
            pass
        try:
            subprocess.run(["pkill", "-9", "ollama"], stderr=subprocess.DEVNULL)
            time.sleep(0.5)
            env = os.environ.copy()
            env["OLLAMA_NUM_PARALLEL"] = "1"
            env["OLLAMA_VULKAN"] = "0"
            env["CUDA_VISIBLE_DEVICES"] = ""
            self.ollama_process = subprocess.Popen(
                ["ollama", "serve"], 
                env=env, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if hasattr(os, "setsid") else None
            )
            time.sleep(2)
        except Exception as e:
            print(f"Error al iniciar Ollama: {e}")

    def update_system(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            now = time.time()
            time_delta = now - self._last_disk_time

            disk_io = psutil.disk_io_counters()
            total_disk_speed = 0
            if time_delta > 0 and disk_io and self._last_disk_io:
                read_bytes = disk_io.read_bytes - self._last_disk_io.read_bytes
                write_bytes = disk_io.write_bytes - self._last_disk_io.write_bytes
                total_disk_speed = (read_bytes + write_bytes) / time_delta
                
                self._last_disk_io = disk_io
                self._last_disk_time = now

                if total_disk_speed < 1048576:
                    disk_str = f"{total_disk_speed / 1024:.1f} KB/s"
                else:
                    disk_str = f"{total_disk_speed / 1048576:.2f} MB/s"
            else:
                disk_str = "0 KB/s"

            temp_str = "--°C"
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current:
                                temp_str = f"{entry.current:.1f}°C"
                                break

            net_io = psutil.net_io_counters()
            net_delta = now - self._last_net_time
            if net_delta > 0:
                download_speed = (net_io.bytes_recv - self._last_net_io.bytes_recv) / net_delta
                self._last_net_io = net_io
                self._last_net_time = now
                down_str = f"{download_speed / 1024:.1f} KB/s" if download_speed < 1048576 else f"{download_speed / 1048576:.2f} MB/s"
            else:
                down_str = "0 KB/s"

            self.cpu_bar.setValue(int(cpu))
            self.cpu_label.setText(f"⚡ CPU: {cpu:.0f}%")

            self.ram_bar.setValue(int(ram))
            self.ram_label.setText(f"💾 RAM: {ram:.0f}%")

            disk_val = min(int((total_disk_speed / (10 * 1024 * 1024)) * 100), 100)
            self.disk_bar.setValue(disk_val)
            self.disk_label.setText(f"💽 DISCO (SSD): {disk_str}")

            self.temp_label.setText(f"🌡 TEMP: {temp_str}")
            self.net_label.setText(f"🌐 RED: ↓ {down_str}")

            self.clock.setText(datetime.now().strftime("%H:%M:%S"))
        except Exception:
            pass

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            self.core.set_state("investigating")
            self.chat.send()
            return
        if key == Qt.Key_Escape:
            self.chat.input.clear()
            self.core.set_state("idle")
            return
        text = event.text()
        if text and text.isprintable():
            try:
                self.chat.input.setFocus()
                self.chat.input.insert(text)
                self.core.set_state("investigating")
            except Exception:
                pass
            return
        super().keyPressEvent(event)

    def toggle_voice(self):
        try:
            if hasattr(self.voice, "start"):
                self.voice.start()
            self.core.set_state("listening")
            self.chat.add_message("ARUS: Escuchando...")
        except Exception:
            pass

    def open_learning(self):
        self.core.set_state("learning")
        self.chat.add_message("ARUS: Pensando...")

    def open_memory(self):
        self.core.set_state("speaking")
        self.chat.add_message("ARUS: Voz preparada.")

    def showEvent(self, event):
        self.chat.input.setFocus()
        self.core.set_state("idle")
        super().showEvent(event)

    def destruir_ollama_completo(self):
        try:
            if self.ollama_process:
                self.ollama_process.terminate()
                self.ollama_process.wait(timeout=2)
        except Exception:
            pass
        
        try:
            subprocess.run(["pkill", "-9", "-f", "ollama"], stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def closeEvent(self, event):
        self.destruir_ollama_completo()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ARUSWindow()
    window.show()
    sys.exit(app.exec())
