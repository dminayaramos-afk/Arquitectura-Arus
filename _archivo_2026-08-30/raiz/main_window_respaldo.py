import requests
import subprocess
import os
import time
import json
from datetime import datetime
import psutil

from PySide6.QtCore import Qt, QTimer, QPoint, QEasingCurve, QVariantAnimation, Signal
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QProgressBar, QApplication, QSplitter,
    QListWidget, QListWidgetItem, QMenu, QInputDialog, QMessageBox, QScrollArea,
    QTextBrowser, QTextEdit
)

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None

from arus.interface.core_visual import NeuralCore
from arus.interface.controller import ARUSController
from arus.interface.adaptive import AdaptiveInterface
from arus.devices.profile import DeviceProfile
from arus.core.voice import VoiceCore


class ModernMessageView(QTextBrowser):
    """Componente de texto avanzado que permite selección nativa, copiado y menú contextual."""
    def __init__(self, text="", is_user=False):
        super().__init__()
        self.setPlainText(text)
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        align_style = "background-color: #020B18; color: #00E5FF;" if not is_user else "background-color: #002B40; color: #FFFFFF;"
        self.setStyleSheet(f"""
            QTextBrowser {{
                {align_style}
                border: none;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                padding: 4px;
            }}
        """)
        self.adjust_height()

    def adjust_height(self):
        doc_height = self.document().size().height()
        self.setFixedHeight(int(doc_height + 18))

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #020B18;
                color: #00E5FF;
                border: 1px solid #004D73;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: #004D73;
                color: #FFFFFF;
            }
        """)
        menu.addSeparator()
        act_copy_msg = menu.addAction("📋 Copiar mensaje completo")
        
        action = menu.exec(event.globalPos())
        if action == act_copy_msg:
            QApplication.clipboard().setText(self.toPlainText())


class ChatWidget(QWidget):
    """Widget de chat optimizado con selección moderna de texto y opciones de copiado."""
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.scroll_area_widget = QWidget()
        self.messages_layout = QVBoxLayout()
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(10)
        self.scroll_area_widget.setLayout(self.messages_layout)

        self.container_scroll = QScrollArea()
        self.container_scroll.setWidgetResizable(True)
        self.container_scroll.setWidget(self.scroll_area_widget)
        self.container_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #004D73;
                border-radius: 8px;
                background-color: #01040a;
            }
        """)
        layout.addWidget(self.container_scroll, 1)

        bottom_layout = QHBoxLayout()
        
        self.input = QTextEdit()
        self.input.setFixedHeight(45)
        self.input.setPlaceholderText("Escribe un mensaje a ARUS... (Presiona Enter para enviar)")
        self.input.setStyleSheet("""
            QTextEdit {
                background-color: #020B18;
                color: #00E5FF;
                border: 1px solid #004D73;
                border-radius: 8px;
                padding: 6px;
            }
        """)
        bottom_layout.addWidget(self.input, 1)

        self.btn_send = QPushButton("Enviar")
        self.btn_send.setFixedWidth(80)
        self.btn_send.setFixedHeight(45)
        self.btn_send.clicked.connect(self.send)
        bottom_layout.addWidget(self.btn_send)

        self.btn_copy_all = QPushButton("📋 Copiar Conversación")
        self.btn_copy_all.setFixedHeight(45)
        self.btn_copy_all.setStyleSheet("font-size: 11px; padding: 4px;")
        self.btn_copy_all.clicked.connect(self.copiar_toda_la_conversacion)
        bottom_layout.addWidget(self.btn_copy_all)

        layout.addLayout(bottom_layout)
        self.mensajes_registrados = []

    def add_message(self, sender_text):
        is_user = sender_text.startswith("Usuario:")
        clean_text = sender_text.replace("Usuario:", "").replace("ARUS:", "").strip()
        
        msg_frame = QFrame()
        msg_frame.setStyleSheet("""
            QFrame {
                background-color: #020B18;
                border: 1px solid #004D73;
                border-radius: 8px;
            }
        """)
        
        frame_layout = QVBoxLayout()
        frame_layout.setContentsMargins(8, 8, 8, 8)
        
        header_layout = QHBoxLayout()
        lbl_sender = QLabel("👤 Tú" if is_user else "✨ ARUS")
        lbl_sender.setStyleSheet("font-weight: bold; color: #00E5FF; border: none; font-size: 11px;")
        header_layout.addWidget(lbl_sender, 1)
        
        if not is_user:
            btn_copy_single = QPushButton("📋 Copiar")
            btn_copy_single.setFixedSize(65, 22)
            btn_copy_single.setCursor(Qt.PointingHandCursor)
            btn_copy_single.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #00E5FF;
                    border: 1px solid #004D73;
                    border-radius: 4px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #004D73;
                    color: #FFFFFF;
                }
            """)
            btn_copy_single.clicked.connect(lambda checked, t=clean_text, b=btn_copy_single: self.copiar_texto_rapido(t, b))
            header_layout.addWidget(btn_copy_single)

        frame_layout.addLayout(header_layout)

        txt_view = ModernMessageView(clean_text, is_user)
        frame_layout.addWidget(txt_view)
        
        msg_frame.setLayout(frame_layout)
        self.messages_layout.addWidget(msg_frame)
        self.mensajes_registrados.append(("Usuario" if is_user else "ARUS", clean_text))

    def copiar_texto_rapido(self, texto, boton):
        QApplication.clipboard().setText(texto)
        boton.setText("Copiado ✓")
        QTimer.singleShot(1500, lambda: boton.setText("📋 Copiar"))

    def copiar_toda_la_conversacion(self):
        if not self.mensajes_registrados:
            return
        lineas = []
        for remitente, texto in self.mensajes_registrados:
            lineas.append(f"{remitente}:\n{texto}\n")
        
        conversacion_completa = "\n".join(lineas).strip()
        QApplication.clipboard().setText(conversacion_completa)
        
        self.btn_copy_all.setText("¡Copiado ✓!")
        QTimer.singleShot(2000, lambda: self.btn_copy_all.setText("📋 Copiar Conversación"))

    def send(self):
        texto = self.input.toPlainText().strip()
        if not texto:
            return
        self.input.clear()
        self.add_message(f"Usuario: {texto}")
        
        if hasattr(self.controller, "process"):
            respuesta = self.controller.process(texto)
            if respuesta:
                self.add_message(f"ARUS: {respuesta}")

    def clear(self):
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.mensajes_registrados.clear()


class ChatItemWidget(QWidget):
    def __init__(self, chat_id, title, parent_window):
        super().__init__()
        self.chat_id = chat_id
        self.parent_window = parent_window
        
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 4, 4)
        
        self.lbl_title = QLabel(f"💬 {title}")
        self.lbl_title.setStyleSheet("border: none; color: #00E5FF; font-size: 12px;")
        
        self.btn_dots = QPushButton("⋮")
        self.btn_dots.setFixedSize(24, 24)
        self.btn_dots.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00E5FF;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #004D73;
                border-radius: 4px;
                color: #FFFFFF;
            }
        """)
        self.btn_dots.clicked.connect(self.mostrar_menu_opciones)
        
        layout.addWidget(self.lbl_title, 1)
        layout.addWidget(self.btn_dots)
        self.setLayout(layout)

    def mostrar_menu_opciones(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #020B18;
                color: #00E5FF;
                border: 1px solid #004D73;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #004D73;
                color: #FFFFFF;
            }
        """)
        
        act_share = menu.addAction("🔗 Compartir conversación")
        act_pin = menu.addAction("📌 Fijar")
        act_rename = menu.addAction("✏️ Cambiar nombre")
        act_delete = menu.addAction("🗑 Borrar")
        
        pos = self.btn_dots.mapToGlobal(QPoint(0, self.btn_dots.height()))
        action = menu.exec(pos)
        
        if action == act_rename:
            self.parent_window.renombrar_chat(self.chat_id)
        elif action == act_delete:
            self.parent_window.borrar_chat(self.chat_id)


class NotificationCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, notif_data):
        super().__init__()
        self.data = notif_data
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.dot_indicator = QLabel("🔴" if not self.data.get("read", False) else "⚪")
        self.dot_indicator.setStyleSheet("font-size: 9px; border: none;")

        lbl_icon_title = QLabel(f"{self.data.get('icon', '🔔')} {self.data.get('title', 'Notificación')}")
        lbl_icon_title.setStyleSheet("font-weight: bold; color: #00E5FF; font-size: 11px; border: none;")

        lbl_time = QLabel(self.data.get("time", ""))
        lbl_time.setStyleSheet("color: #0083B0; font-size: 9px; border: none;")

        top_layout.addWidget(self.dot_indicator)
        top_layout.addWidget(lbl_icon_title, 1)
        top_layout.addWidget(lbl_time)

        lbl_detail = QLabel(self.data.get("detail", ""))
        lbl_detail.setWordWrap(True)
        lbl_detail.setStyleSheet("color: #B0E6FF; font-size: 10px; border: none;")

        layout.addLayout(top_layout)
        layout.addWidget(lbl_detail)
        self.setLayout(layout)

    def update_style(self):
        if not self.data.get("read", False):
            self.setStyleSheet("""
                NotificationCard {
                    background-color: #03152A;
                    border: 1px solid #00E5FF;
                    border-radius: 6px;
                }
                NotificationCard:hover {
                    background-color: #002B40;
                }
            """)
        else:
            self.setStyleSheet("""
                NotificationCard {
                    background-color: #010A14;
                    border: 1px solid #004D73;
                    border-radius: 6px;
                }
                NotificationCard:hover {
                    background-color: #021224;
                }
            """)

    def mark_as_read(self):
        self.data["read"] = True
        self.dot_indicator.setText("⚪")
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mark_as_read()
            self.clicked.emit(self.data)
        super().mousePressEvent(event)


class ARUSActivityWidget(QFrame):
    action_triggered = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.is_maximized = False
        self.default_width = 300
        self.default_height = 350
        
        self.setFixedWidth(self.default_width)
        self.setFixedHeight(self.default_height)
        self.setStyleSheet("""
            ARUSActivityWidget {
                background-color: #020B18;
                border: 1px solid #00E5FF;
                border-radius: 10px;
            }
        """)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(10, 8, 10, 8)
        self.main_layout.setSpacing(6)
        self.setLayout(self.main_layout)

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_panel_title = QLabel("🔔 Centro de Actividad")
        self.lbl_panel_title.setStyleSheet("font-weight: bold; color: #00E5FF; font-size: 12px; border: none;")

        self.btn_expand = QPushButton("🗖")
        self.btn_expand.setFixedSize(22, 22)
        self.btn_expand.setCursor(Qt.PointingHandCursor)
        self.btn_expand.setStyleSheet("QPushButton { background-color: transparent; color: #00E5FF; border: none; font-weight: bold; font-size: 12px; } QPushButton:hover { background-color: #004D73; color: #FFFFFF; border-radius: 4px; }")
        self.btn_expand.clicked.connect(self.toggle_expand_size)

        self.btn_close = QPushButton("✖")
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_close.setStyleSheet("QPushButton { background-color: transparent; color: #00E5FF; border: none; font-weight: bold; font-size: 13px; } QPushButton:hover { background-color: #004D73; color: #FFFFFF; border-radius: 4px; }")
        self.btn_close.clicked.connect(self.hide_panel)

        self.header_layout.addWidget(self.lbl_panel_title, 1)
        self.header_layout.addWidget(self.btn_expand)
        self.header_layout.addWidget(self.btn_close)
        self.main_layout.addLayout(self.header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.cards_holder = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(6)
        self.cards_layout.addStretch()
        self.cards_holder.setLayout(self.cards_layout)

        self.scroll_area.setWidget(self.cards_holder)
        self.main_layout.addWidget(self.scroll_area)
        self.setVisible(False)

    def hide_panel(self):
        self.setVisible(False)

    def toggle_panel(self):
        self.setVisible(not self.isVisible())
        if self.isVisible():
            self.raise_()

    def toggle_expand_size(self):
        self.is_maximized = not self.is_maximized
        if self.parent():
            parent_h = self.parent().height()
            if self.is_maximized:
                target_w = 380
                target_h = max(450, parent_h - 40)
                self.btn_expand.setText("🗗")
            else:
                target_w = self.default_width
                target_h = self.default_height
                self.btn_expand.setText("🗖")

            self.setFixedWidth(target_w)
            self.setFixedHeight(target_h)
            self.move(15, parent_h - target_h - 15)

    def add_notification(self, category, title, detail, time_str="", metadata=None):
        icons = {"msg": "💬", "reminder": "⏰", "note": "🧠", "file": "📂", "search": "🔎", "task": "✅", "alert": "⚠️"}
        notif = {
            "type": category,
            "icon": icons.get(category, "🔔"),
            "title": title,
            "detail": detail,
            "time": time_str if time_str else datetime.now().strftime("%H:%M"),
            "read": False,
            "metadata": metadata or {}
        }
        self.notifications.insert(0, notif)
        card = NotificationCard(notif)
        card.clicked.connect(self._on_card_clicked)
        self.cards_layout.insertWidget(0, card)

    def _on_card_clicked(self, notif_data):
        self.action_triggered.emit(notif_data)


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

        self.history_file = "chat_history.json"
        self.current_chat_id = None
        self.history_target_width = 260
        self.is_history_open = False

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
            QLabel { background-color: transparent; color: #00E5FF; }
            QProgressBar {
                background-color: #01040a; color: #FFFFFF; border: 1px solid #004D73;
                border-radius: 5px; text-align: center; height: 12px; font-size: 10px; font-weight: bold;
            }
            QProgressBar::chunk { background-color: #00E5FF; border-radius: 4px; }
            QPushButton {
                background-color: #020B18; color: #00E5FF; border: 1px solid #004D73;
                border-radius: 8px; padding: 8px; font-weight: bold;
            }
            QPushButton:hover { background-color: #004D73; color: #FFFFFF; }
            QSplitter::handle { background-color: #004D73; border-radius: 3px; margin: 2px; }
            QListWidget { background-color: #01040a; border: 1px solid #004D73; border-radius: 5px; color: #00E5FF; }
            QListWidget::item:selected { background-color: #002B40; border-radius: 5px; }
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

        self.left_top_widget = QWidget()
        self.left_top_layout = QHBoxLayout()
        self.left_top_layout.setContentsMargins(0, 0, 0, 0)
        self.left_top_widget.setLayout(self.left_top_layout)

        self.btn_history = QPushButton("📜 Historial")
        self.btn_history.setFixedHeight(30)
        self.btn_history.clicked.connect(self.toggle_history_panel)

        self.lbl_sub_status = QLabel("CORE ONLINE")
        self.lbl_sub_status.setStyleSheet("font-size: 11px; color: #004D73; border: none;")

        self.left_top_layout.addWidget(self.btn_history)
        self.left_top_layout.addWidget(self.lbl_sub_status)
        self.left_top_layout.addStretch()

        self.btn_title = QPushButton("◈   A R U S   ◈")
        self.btn_title.setCursor(Qt.PointingHandCursor)
        self.btn_title.setStyleSheet("QPushButton { background: transparent; border: none; font-size: 20px; font-weight: bold; color: #00E5FF; letter-spacing: 4px; } QPushButton:hover { color: #FFFFFF; }")
        self.btn_title.clicked.connect(self.toggle_activity_center)

        self.right_top_widget = QWidget()
        self.right_top_layout = QHBoxLayout()
        self.right_top_layout.setContentsMargins(0, 0, 0, 0)
        self.right_top_widget.setLayout(self.right_top_layout)

        self.lbl_clock = QLabel("--:--:--")
        self.lbl_clock.setStyleSheet("font-family: monospace; font-size: 13px; border: none;")
        self.clock = self.lbl_clock

        self.right_top_layout.addStretch()
        self.right_top_layout.addWidget(self.lbl_clock)

        self.top_layout.addWidget(self.left_top_widget, 1)
        self.top_layout.addWidget(self.btn_title, 1)
        self.top_layout.addWidget(self.right_top_widget, 1)
        self.main_layout.addWidget(self.top_bar)

        self.body_widget = QWidget()
        self.body_layout = QHBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(15)
        self.body_widget.setLayout(self.body_layout)
        self.main_layout.addWidget(self.body_widget, 1)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.body_layout.addWidget(self.main_splitter)

        # Historial con botón Nuevo Chat
        self.history_panel = QFrame()
        self.history_panel_layout = QVBoxLayout()
        self.history_panel.setLayout(self.history_panel_layout)

        hist_header_layout = QHBoxLayout()
        lbl_hist_title = QLabel("Recientes")
        lbl_hist_title.setStyleSheet("font-weight: bold; color: #00E5FF; font-size: 14px; border: none;")
        
        self.btn_new_chat = QPushButton("➕ Nuevo chat")
        self.btn_new_chat.setFixedHeight(26)
        self.btn_new_chat.setCursor(Qt.PointingHandCursor)
        self.btn_new_chat.setStyleSheet("QPushButton { font-size: 11px; padding: 2px 8px; }")
        self.btn_new_chat.clicked.connect(self.nuevo_chat)

        hist_header_layout.addWidget(lbl_hist_title, 1)
        hist_header_layout.addWidget(self.btn_new_chat)
        self.history_panel_layout.addLayout(hist_header_layout)

        self.list_history = QListWidget()
        self.history_panel_layout.addWidget(self.list_history)
        self.list_history.itemClicked.connect(self.cargar_chat_seleccionado)
        self.main_splitter.addWidget(self.history_panel)

        self.core = NeuralCore()
        self.core.setMinimumSize(400, 400)
        self.main_splitter.addWidget(self.core)

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

        self.btn_layout = QHBoxLayout()
        self.btn_listen = QPushButton("🎤 Escuchar")
        self.btn_think = QPushButton("🧠 Pensar")
        self.btn_speak = QPushButton("🗣 Hablar")

        self.btn_layout.addWidget(self.btn_listen)
        self.btn_layout.addWidget(self.btn_think)
        self.btn_layout.addWidget(self.btn_speak)
        self.sys_layout.addLayout(self.btn_layout)

        self.chat_splitter.addWidget(self.sys_container)
        self.main_splitter.addWidget(self.right_panel)

        self.main_splitter.setSizes([0, 850, 450])
        self.chat_splitter.setSizes([430, 250])

        self.btn_listen.clicked.connect(self.toggle_voice)
        self.btn_think.clicked.connect(self.open_learning)
        self.btn_speak.clicked.connect(self.open_memory)

        self.activity_center = ARUSActivityWidget(self.central)
        self.activity_center.action_triggered.connect(self.atender_notificacion)

        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system)
        self.system_timer.start(1000)

        self.core.set_state("idle")
        self.chat.add_message("ARUS: Conectado. Búsqueda web habilitada.")
        self.cargar_lista_historial()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "activity_center"):
            act_h = self.activity_center.height()
            self.activity_center.move(15, self.height() - act_h - 15)

    def toggle_activity_center(self):
        self.activity_center.toggle_panel()
        if hasattr(self, "activity_center"):
            act_h = self.activity_center.height()
            self.activity_center.move(15, self.height() - act_h - 15)

    def atender_notificacion(self, notif_data):
        titulo = notif_data.get("title", "")
        detalle = notif_data.get("detail", "")
        self.chat.add_message(f"ARUS [Sistema]: Notificación '{titulo}' - {detalle}")

    def toggle_history_panel(self):
        sizes = self.main_splitter.sizes()
        start_w = sizes[0]
        end_w = self.history_target_width if not self.is_history_open else 0
        total_restante = sum(sizes[1:])
        if total_restante == 0:
            total_restante = 1

        self.anim = QVariantAnimation()
        self.anim.setDuration(250)
        self.anim.setStartValue(start_w)
        self.anim.setEndValue(end_w)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        def update_sizes(value):
            current_w = int(value)
            s1 = int(sizes[1] * (sum(sizes) - current_w) / total_restante)
            s2 = sum(sizes) - current_w - s1
            self.main_splitter.setSizes([current_w, s1, s2])

        self.anim.valueChanged.connect(update_sizes)
        self.anim.start()
        self.is_history_open = not self.is_history_open

    def obtener_conversaciones(self):
        if not os.path.exists(self.history_file):
            return {}
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def guardar_conversaciones(self, data):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar historial: {e}")

    def cargar_lista_historial(self):
        self.list_history.clear()
        conversaciones = self.obtener_conversaciones()
        for chat_id, data in conversaciones.items():
            item = QListWidgetItem(self.list_history)
            item.setData(Qt.UserRole, chat_id)
            titulo = data.get('titulo', chat_id)
            item_widget = ChatItemWidget(chat_id, titulo, self)
            item.setSizeHint(item_widget.sizeHint())
            self.list_history.addItem(item)
            self.list_history.setItemWidget(item, item_widget)

    def cargar_chat_seleccionado(self, item):
        chat_id = item.data(Qt.UserRole)
        conversaciones = self.obtener_conversaciones()
        if chat_id in conversaciones:
            self.current_chat_id = chat_id
            if hasattr(self.chat, "clear"):
                self.chat.clear()
            for msg in conversaciones[chat_id].get("mensajes", []):
                self.chat.add_message(msg)

    def nuevo_chat(self):
        self.current_chat_id = None
        if hasattr(self.chat, "clear"):
            self.chat.clear()
        self.chat.add_message("ARUS: Nueva conversación iniciada.")
        if hasattr(self.chat, "input"):
            self.chat.input.setFocus()

    def borrar_chat(self, chat_id):
        conversaciones = self.obtener_conversaciones()
        if chat_id in conversaciones:
            del conversaciones[chat_id]
            self.guardar_conversaciones(conversaciones)
            if self.current_chat_id == chat_id:
                self.current_chat_id = None
                if hasattr(self.chat, "clear"):
                    self.chat.clear()
            self.cargar_lista_historial()

    def renombrar_chat(self, chat_id):
        conversaciones = self.obtener_conversaciones()
        if chat_id in conversaciones:
            titulo_actual = conversaciones[chat_id].get("titulo", "")
            nuevo_nombre, ok = QInputDialog.getText(self, "Cambiar nombre", "Nuevo nombre de la conversación:", text=titulo_actual)
            if ok and nuevo_nombre.strip():
                conversaciones[chat_id]["titulo"] = nuevo_nombre.strip()
                self.guardar_conversaciones(conversaciones)
                self.cargar_lista_historial()

    def guardar_mensaje_actual(self, mensaje):
        if not self.current_chat_id:
            self.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            titulo_auto = mensaje.replace("Usuario: ", "").strip()
            if len(titulo_auto) > 25:
                titulo_auto = titulo_auto[:25] + "..."
            
            conversaciones = self.obtener_conversaciones()
            conversaciones[self.current_chat_id] = {
                "titulo": titulo_auto if titulo_auto else f"Chat {datetime.now().strftime('%d/%m %H:%M')}",
                "mensajes": []
            }
        else:
            conversaciones = self.obtener_conversaciones()
            if self.current_chat_id not in conversaciones:
                conversaciones[self.current_chat_id] = {
                    "titulo": f"Chat {datetime.now().strftime('%d/%m %H:%M')}",
                    "mensajes": []
                }
        
        conversaciones[self.current_chat_id]["mensajes"].append(mensaje)
        self.guardar_conversaciones(conversaciones)
        self.cargar_lista_historial()

    def iniciar_ollama_automatico(self):
        try:
            res = requests.get("http://localhost:11434/", timeout=1)
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
                ["ollama", "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid if hasattr(os, "setsid") else None
            )
            time.sleep(2)
        except Exception as e:
            print(f"Error al iniciar Ollama: {e}")

    def update_system(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.cpu_bar.setValue(int(cpu))
            self.cpu_label.setText(f"⚡ CPU: {cpu:.0f}%")
            self.ram_bar.setValue(int(ram))
            self.ram_label.setText(f"💾 RAM: {ram:.0f}%")
            self.clock.setText(datetime.now().strftime("%H:%M:%S"))
        except Exception:
            pass

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
