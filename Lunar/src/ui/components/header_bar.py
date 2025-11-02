from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QFrame,
                              QPushButton, QVBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QIcon
import os

class HeaderBar(QFrame):
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
        self.message_btn = self.create_icon_button("message.png", "Messages")
        layout.addWidget(self.message_btn)

        # Botão de notificação
        self.notification_btn = self.create_icon_button("no_notification.png", "Notifications")
        layout.addWidget(self.notification_btn)

        # Nome do usuário
        user_widget = self.create_user_widget()
        layout.addWidget(user_widget)

        return section

    def create_icon_button(self, icon_filename, tooltip):
        btn = QPushButton()
        btn.setObjectName("iconButton")
        btn.setFixedSize(32, 32)  # Tamanho reduzido para ficar mais discreto
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)

        # Carregar ícone - caminho correto
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'icons', icon_filename)
        
        # Se não encontrar nos assets, tenta na pasta icons local
        if not os.path.exists(icon_path):
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', icon_filename)
        
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
        else:
            # Fallback para texto se ícone não existir
            print(f"Ícone não encontrado: {icon_path}")
            btn.setText("📧" if "message" in icon_filename else "🔔")

        return btn

    def create_user_widget(self):
        widget = QFrame()
        widget.setObjectName("userWidget")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)  # Margens reduzidas
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
