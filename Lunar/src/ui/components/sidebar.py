from PySide6.QtWidgets import (QFrame, QVBoxLayout, QPushButton,
                              QLabel, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QIcon
import os

class Sidebar(QFrame):
    navigation_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = "dashboard"
        self.setup_ui()

    def setup_ui(self):
        """Configura a sidebar mais estreita"""
        self.setFixedWidth(120)  # Reduzida de 260 para 200
        self.setObjectName("sidebar")

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header removido (agora está no HeaderBar)

        # Logo no topo
        logo_header = self.create_logo_header()
        layout.addWidget(logo_header)

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

    def create_logo_header(self):
        """Cria o header da sidebar com o logo"""
        logo_label = QLabel()
        logo_label.setObjectName("sidebarLogo")
        logo_label.setFixedHeight(80) # Altura similar ao header_bar
        logo_label.setAlignment(Qt.AlignCenter)

        # Carregar ícone - caminho correto
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'icons', 'logo.png')

        if not os.path.exists(icon_path):
             # Fallback para pasta local de icons
             icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', 'logo.png')

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            print(f"Logo não encontrado: {icon_path}")
            logo_label.setText("LUNAR") # Fallback
            logo_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
            logo_label.setStyleSheet("color: white;")

        return logo_label

    def create_navigation_buttons(self):
        """Cria botões de navegação minimalistas"""
        nav_frame = QFrame()
        nav_frame.setObjectName("navFrame")

        layout = QVBoxLayout(nav_frame)
        layout.setContentsMargins(10, 20, 10, 20)  # Margens reduzidas
        layout.setSpacing(6) # Espaçamento dobrado (3 -> 6)

        # Botões atualizados
        nav_items = [
            # (Texto p/ ToolTip, page_id, icon_filename, is_active)
            ("Dashboard", "dashboard", "dashboard.png", True),
            ("Security Tools", "tools", "stools.png", False),
            ("System Info", "system_info", "sinfo.png", False),
            ("Settings", "settings", "settings.png", False)
        ]

        self.nav_buttons = {}

        for text, page_id, icon_name, is_active in nav_items:
            btn = QPushButton() # Criar botão sem texto
            btn.setToolTip(text) # Adicionar o texto como dica
            btn.setObjectName(f"navButton_{page_id}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(108)  # Altura aumentada (72 -> 108)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            # Lógica para adicionar ícone
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'assets', 'icons', icon_name)

            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', icon_name)

            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(54, 54)) # Ícone aumentado (36 -> 54)
            else:
                print(f"Ícone de navegação não encontrado: {icon_path}")
                btn.setText(text) # Fallback para texto se ícone falhar

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
