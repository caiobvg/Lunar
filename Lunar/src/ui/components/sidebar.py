from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                              QLabel, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor
import os

class Sidebar(QWidget):
    navigation_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = "dashboard"
        self.setup_ui()

    def setup_ui(self):
        """Configura a sidebar mais estreita"""
        self.setFixedWidth(200)  # Reduzida de 260 para 200
        self.setObjectName("sidebar")

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header removido (agora está no HeaderBar)

        # Navegação limpa
        nav_buttons = self.create_navigation_buttons()
        layout.addWidget(nav_buttons)

        # Espaço flexível
        layout.addStretch(1)

        # Footer minimalista
        footer = self.create_footer()
        layout.addWidget(footer)

    def create_header(self):
        """Cria cabeçalho minimalista"""
        header_frame = QFrame()
        header_frame.setObjectName("sidebarHeader")
        header_frame.setFixedHeight(100)

        layout = QVBoxLayout(header_frame)
        layout.setContentsMargins(20, 20, 20, 15)

        # Logo elegante
        logo_label = QLabel("LUNAR")
        logo_label.setObjectName("logoLabel")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(QFont("Segoe UI", 18, QFont.Bold))

        # Subtítulo sutil
        subtitle_label = QLabel("SYSTEM PROTECTION")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 8))

        layout.addWidget(logo_label)
        layout.addWidget(subtitle_label)

        return header_frame

    def create_navigation_buttons(self):
        """Cria botões de navegação minimalistas"""
        nav_frame = QFrame()
        nav_frame.setObjectName("navFrame")

        layout = QVBoxLayout(nav_frame)
        layout.setContentsMargins(10, 20, 10, 20)  # Margens reduzidas
        layout.setSpacing(2)

        # Botões atualizados
        nav_items = [
            ("Dashboard", "dashboard", True),
            ("Security Tools", "tools", False),
            ("System Info", "system_info", False),
            ("Settings", "settings", False),
            ("Support", "support", False)
        ]

        self.nav_buttons = {}

        for text, page_id, is_active in nav_items:
            btn = QPushButton(text)
            btn.setObjectName(f"navButton_{page_id}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(38)  # Altura reduzida
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # Conectar sinal
            btn.clicked.connect(lambda checked, pid=page_id: self.on_navigation_click(pid))

            # Estado ativo
            if is_active:
                self.set_button_active(btn, True)

            layout.addWidget(btn)
            self.nav_buttons[page_id] = btn

        return nav_frame

    def create_footer(self):
        """Cria rodapé minimalista"""
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_frame.setFixedHeight(60)

        layout = QVBoxLayout(footer_frame)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Status
        status_label = QLabel("● SECURE")
        status_label.setObjectName("statusLabel")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFont(QFont("Segoe UI", 9, QFont.Bold))

        layout.addStretch(1)
        layout.addWidget(status_label)

        return footer_frame

    def on_navigation_click(self, page_id):
        """Handler para navegação"""
        # Atualizar estados dos botões
        for pid, btn in self.nav_buttons.items():
            self.set_button_active(btn, pid == page_id)

        self.current_page = page_id
        self.navigation_changed.emit(page_id)

    def set_button_active(self, button, active):
        """Define estado ativo do botão"""
        button.setProperty("active", "true" if active else "false")
        button.style().unpolish(button)
        button.style().polish(button)
