from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QFrame,
                              QVBoxLayout, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os

class HeaderBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)  # Altura reduzida
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("headerBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 15, 30, 15)
        layout.setSpacing(0)

        # Logo e título à esquerda
        logo_section = self.create_logo_section()
        layout.addWidget(logo_section)

        # Espaço flexível no meio
        layout.addStretch(1)

        # Botões à direita
        buttons_section = self.create_buttons_section()
        layout.addWidget(buttons_section)

    def create_logo_section(self):
        section = QFrame()
        section.setObjectName("logoSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title = QLabel("LUNAR SYSTEM PROTECTION")
        title.setObjectName("headerTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        subtitle = QLabel("Advanced Security Suite")
        subtitle.setObjectName("headerSubtitle")
        subtitle.setFont(QFont("Segoe UI", 10))

        layout.addWidget(title)
        layout.addWidget(subtitle)

        return section

    def create_buttons_section(self):
        section = QFrame()
        section.setObjectName("buttonsSection")
        layout = QHBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # Botão de mensagem
        self.message_btn = self.create_icon_button("💬", "Messages")
        layout.addWidget(self.message_btn)

        # Botão de notificação
        self.notification_btn = self.create_icon_button("🔔", "Notifications")
        layout.addWidget(self.notification_btn)

        # Nome do usuário
        user_widget = self.create_user_widget()
        layout.addWidget(user_widget)

        return section

    def create_icon_button(self, icon, tooltip):
        btn = QPushButton(icon)
        btn.setObjectName("iconButton")
        btn.setFixedSize(40, 40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)
        return btn

    def create_user_widget(self):
        widget = QFrame()
        widget.setObjectName("userWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)

        user_label = QLabel("User")
        user_label.setObjectName("userLabel")
        user_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        role_label = QLabel("Administrator")
        role_label.setObjectName("roleLabel")
        role_label.setFont(QFont("Segoe UI", 9))

        layout.addWidget(user_label)
        layout.addWidget(role_label)

        return widget
