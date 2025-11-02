from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QStatusBar, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import os

from src.ui.components.sidebar import Sidebar
from src.ui.components.dashboard import Dashboard
from src.ui.components.particles import ParticleSystem
from src.ui.components.header_bar import HeaderBar  # Novo componente

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

        # Estilo mínimo inicial
        self.setStyleSheet("background-color: #000000; color: white;")

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
            print("Interface Lunar com particulas carregada")
        except Exception as e:
            print(f"Erro na UI: {e}")
            self.setup_fallback_ui()

    def setup_ui(self):
        """Configura a interface completa com partículas de fundo"""
        # Widget central
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # HeaderBar no topo
        self.header_bar = HeaderBar()
        main_layout.addWidget(self.header_bar)

        # Área de conteúdo (sidebar + conteúdo)
        content_area = QWidget()
        content_area.setObjectName("contentArea")
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sistema de partículas como fundo
        self.particle_system = ParticleSystem(central_widget)
        self.particle_system.lower()  # Garante que fique atrás de tudo

        # Sidebar (mais estreita)
        self.sidebar = Sidebar()
        content_layout.addWidget(self.sidebar)

        # Área de conteúdo principal
        self.content_stack = QWidget()
        self.content_stack.setObjectName("contentStack")
        content_stack_layout = QVBoxLayout(self.content_stack)
        content_stack_layout.setContentsMargins(0, 0, 0, 0)
        content_stack_layout.setSpacing(0)

        # Dashboard
        self.dashboard = Dashboard(self.controller)
        content_stack_layout.addWidget(self.dashboard)

        content_layout.addWidget(self.content_stack)

        main_layout.addWidget(content_area)

        # Conectar navegação
        self.sidebar.navigation_changed.connect(self.on_navigation_changed)

        # Barra de status
        self.setup_status_bar()

    def on_navigation_changed(self, page_id):
        """Handler de navegação"""
        self.current_page = page_id

        status_messages = {
            "dashboard": "Dashboard - System overview and security controls",
            "tools": "Tools - Advanced system utilities",
            "system_info": "System Info - Hardware and software information",
            "settings": "Settings - Application configuration",
            "discord": "Discord - Contact and support information"
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
        layout.addWidget(error_label)

    def setup_status_bar(self):
        """Configura barra de status"""
        status_bar = QStatusBar()
        status_bar.showMessage("Lunar Spoofer initialized - Carbon theme active")
        self.setStatusBar(status_bar)

    def load_stylesheet(self):
        """Carrega CSS atualizado"""
        try:
            css_path = os.path.join(os.path.dirname(__file__), 'styles', 'main.css')
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
                print("CSS estelar com particulas aplicado")
            else:
                self.apply_fallback_styles()
        except Exception as e:
            print(f"CSS error: {e}")
            self.apply_fallback_styles()

    def apply_fallback_styles(self):
        """Estilos de fallback"""
        fallback_css = """
            QMainWindow {
                background-color: #000000;
                color: #ffffff;
                font-family: "Segoe UI";
            }
            QStatusBar {
                background-color: #1a1a1a;
                color: #b0b0b0;
                padding: 8px;
            }
        """
        self.setStyleSheet(fallback_css)

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
