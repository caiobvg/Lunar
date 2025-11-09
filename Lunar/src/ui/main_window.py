from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QStatusBar, QMessageBox, QLabel, QFrame,
                              QPushButton)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
import os

from src.ui.components.sidebar import Sidebar
from src.ui.components.dashboard import Dashboard
from src.ui.components.particles import ParticleSystem
import traceback

class MainWindow(QMainWindow):
    def __init__(self, spoofer_controller):
        super().__init__()
        self.controller = spoofer_controller
        self.current_page = "dashboard"

        self.setup_window()
        QTimer.singleShot(100, self.initialize_ui)

    def setup_window(self):
        """Configuração da janela principal"""
        self.setWindowTitle("Lunar Spoofer - Advanced System Protection")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # Aplicar fundo básico
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; }")
        
        self.center_on_screen()

    def center_on_screen(self):
        """Centraliza a janela"""
        screen = self.screen().availableGeometry()
        window_size = self.frameGeometry()
        self.move(
            (screen.width() - window_size.width()) // 2,
            (screen.height() - window_size.height()) // 2
        )

    def initialize_ui(self):
        """Inicializa a UI com partículas"""
        try:
            self.setup_ui()
            self.load_stylesheet()
            print("Interface Lunar com partículas carregada")

            # Inicializar partículas após um pequeno delay
            QTimer.singleShot(100, self.initialize_particles)

        except Exception as e:
            print(f"Erro na UI: {e}")
            self.setup_fallback_ui()

    def setup_ui(self):
        """Configura a interface completa"""
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # Layout principal (REMOVIDO PARA PERMITIR SOBREPOSIÇÃO)
        # main_layout = QVBoxLayout(central_widget)
        # main_layout.setContentsMargins(0, 0, 0, 0)
        # main_layout.setSpacing(0)

        # Sistema de partículas como overlay transparente - FUNDO
        self.particle_system = ParticleSystem(central_widget)

        # HeaderBar REMOVED

        # Área de conteúdo principal
        self.content_stack = QFrame(central_widget)
        self.content_stack.setObjectName("contentStack")
        content_stack_layout = QVBoxLayout(self.content_stack)
        content_stack_layout.setContentsMargins(0, 0, 0, 0)
        content_stack_layout.setSpacing(0)

        # Dashboard
        self.dashboard = Dashboard(self.controller)
        content_stack_layout.addWidget(self.dashboard)

        # Sidebar (CAMADA SUPERIOR)
        self.sidebar = Sidebar(central_widget)

        # Floating buttons (header buttons moved here)
        self.message_btn = self.create_icon_button("message.png", "Messages")
        self.message_btn.setParent(central_widget)

        self.notification_btn = self.create_icon_button("no_notification.png", "Notifications")
        self.notification_btn.setParent(central_widget)

        self.user_widget = self.create_user_widget()
        self.user_widget.setParent(central_widget)

        # Barra de status
        self.setup_status_bar()

        # Conectar navegação
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)

        # Chamar a lógica de posicionamento pela primeira vez
        self.update_geometries()

    def on_navigation_changed(self, page_id):
        """Handler de navegação"""
        self.current_page = page_id

        status_messages = {
            "dashboard": "Dashboard - System overview and security controls",
            "tools": "Tools - Advanced system utilities",
            "system_info": "System Info - Hardware and software information",
            "settings": "Settings - Application configuration"
        }

        self.statusBar().showMessage(status_messages.get(page_id, "System ready"))
        print(f"Navegando para: {page_id}")

    def setup_fallback_ui(self):
        """UI de fallback"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        error_label = QLabel("System interface compatibility mode")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: white;")
        layout.addWidget(error_label)

    def setup_status_bar(self):
        """Configura barra de status"""
        status_bar = QStatusBar()
        status_bar.showMessage("Lunar Spoofer initialized - Modern theme active")
        self.setStatusBar(status_bar)

    def resizeEvent(self, event):
        """Gerencia a geometria dos componentes para sobreposição"""
        super().resizeEvent(event)
        self.update_geometries()

    def update_geometries(self):
        """Posiciona os widgets manualmente para permitir sobreposição"""
        w = self.width()
        h = self.height()

        # 1. Partículas (fundo)
        if hasattr(self, 'particle_system'):
            self.particle_system.setGeometry(0, 0, w, h)
            self.particle_system.lower()

        # 2. Content Stack (starts at top now, behind sidebar)
        if hasattr(self, 'content_stack'):
            if hasattr(self, 'sidebar'):
                sidebar_width = self.sidebar.width()
                self.content_stack.setGeometry(
                    sidebar_width,
                    0,  # Starts at Y=0
                    w - sidebar_width,
                    h  # Occupies full height
                )
            else:
                self.content_stack.setGeometry(0, 0, w, h)

        # 4. Sidebar (topo)
        if hasattr(self, 'sidebar'):
            sidebar_width = self.sidebar.width() # Pega a largura fixa (150)
            # A sidebar começa em (0, 0) e ocupa a altura total
            self.sidebar.setGeometry(0, 0, sidebar_width, h)
            self.sidebar.raise_() # Coloca a sidebar no topo

        # 5. Floating buttons (positioned in top-right corner)
        margin = 30
        spacing = 15
        button_size = 40 # AUMENTADO DE 32 para 40

        if hasattr(self, 'user_widget'):
            user_width = self.user_widget.width()
            user_height = self.user_widget.height()

            # Centralizar verticalmente os botões em relação ao user_widget
            button_y = margin + (user_height / 2) - (button_size / 2)

            # Posicionar User Widget
            self.user_widget.setGeometry(w - user_width - margin, margin, user_width, user_height)
            self.user_widget.raise_()

            if hasattr(self, 'notification_btn'):
                # Usar button_size e button_y
                self.notification_btn.setGeometry(
                    w - user_width - margin - button_size - spacing,
                    button_y,
                    button_size,
                    button_size
                )
                self.notification_btn.raise_()

                if hasattr(self, 'message_btn'):
                    # Usar button_size e button_y
                    self.message_btn.setGeometry(
                        w - user_width - margin - button_size - spacing - button_size - spacing,
                        button_y,
                        button_size,
                        button_size
                    )
                    self.message_btn.raise_()

    # Methods moved from header_bar.py

    def create_icon_button(self, icon_filename, tooltip):
        btn = QPushButton()
        btn.setObjectName("iconButton")  # CSS will still work
        btn.setFixedSize(40, 40) # AUMENTADO DE 32, 32
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(tooltip)

        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icons', icon_filename)

        if not os.path.exists(icon_path):
           icon_path = os.path.join(os.path.dirname(__file__), '..', 'icons', icon_filename)

        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # AUMENTADO DE 24, 24 para 30, 30
            pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(pixmap.size())
        else:
            print(f"Ícone não encontrado: {icon_path}")
            btn.setText("📧" if "message" in icon_filename else "🔔")
        return btn

    def create_user_widget(self):
        widget = QFrame()
        widget.setObjectName("userWidget")  # CSS will still work
        layout = QVBoxLayout(widget)
        # AUMENTADO MARGENS de (8, 4, 8, 4) para (10, 6, 10, 6)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)

        user_label = QLabel("User")
        user_label.setObjectName("userLabel")
        # AUMENTADO FONTE de 12 para 15
        user_label.setFont(QFont("Segoe UI", 15, QFont.Bold))

        role_label = QLabel("Administrator")
        role_label.setObjectName("roleLabel")
        # AUMENTADO FONTE de 9 para 11
        role_label.setFont(QFont("Segoe UI", 11))

        layout.addWidget(user_label)
        layout.addWidget(role_label)
        widget.setFixedSize(widget.sizeHint())  # Define fixed size
        return widget

    def initialize_particles(self):
        """Inicializa e posiciona o sistema de partículas"""
        if hasattr(self, 'particle_system'):
            self.particle_system.setGeometry(0, 0, self.width(), self.height())
            self.particle_system.update()

    def load_stylesheet(self):
        """Carrega CSS atualizado de forma mais robusta"""
        try:
            # Constrói um caminho absoluto para o arquivo CSS
            current_dir = os.path.dirname(os.path.abspath(__file__))
            css_path = os.path.join(current_dir, 'styles', 'main.css')

            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    # Aplicar CSS
                    self.setStyleSheet(css_content)
                print(f"CSS aplicado com sucesso de: {css_path}")
            else:
                print(f"ERRO: Arquivo CSS não encontrado em: {css_path}")
                self.apply_minimal_styles()
        except Exception as e:
            print(f"Erro ao carregar CSS: {e}")
            self.apply_minimal_styles()

    def apply_minimal_styles(self):
        """Aplica estilos mínimos para garantir funcionamento"""
        minimal_css = """
            QMainWindow {
                background-color: #1a1a1a;
                color: #ffffff;
            }

            /* ===== ESTILOS DO HEADER ADICIONADOS AQUI ===== */
            #headerBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2d2d2d, stop:1 #3a3a3a);
                border-bottom: 2px solid #4a4a4a;
                outline: none;
            }
            #headerTitle {
                color: #ffffff;
                background: transparent;
                font-size: 16px;
                font-weight: bold;
            }
            #headerSubtitle {
                color: #cccccc;
                background: transparent;
                font-size: 10px;
            }
            #userLabel {
                color: #ffffff;
                background: transparent;
            }
            #roleLabel {
                color: #cccccc;
                background: transparent;
            }
            /* ============================================== */

            QPushButton#mainSpoofButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a90e2, stop:1 #50e3c2);
                color: #000000;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 14px 28px;
            }
            QPushButton#mainSpoofButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5a9fee, stop:1 #60f3d2);
            }
            QLabel#hardwareValue {
                font-size: 16px;
                font-weight: bold;
            }
        """
        self.setStyleSheet(minimal_css)

    def closeEvent(self, event):
        """Handler de fechamento"""
        reply = QMessageBox.question(
            self, 'Exit Confirmation',
            'Are you sure you want to exit Lunar Spoofer?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
