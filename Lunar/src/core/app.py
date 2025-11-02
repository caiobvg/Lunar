import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

class LunarApp:
    def __init__(self):
        # Criar QApplication PRIMEIRO
        self.qt_app = QApplication(sys.argv)
        self.main_window = None

        # Configuração básica
        self.setup_application()

    def setup_application(self):
        """Configurações iniciais seguras"""
        self.qt_app.setApplicationName("Lunar Spoofer")
        self.qt_app.setApplicationVersion("1.0.0")

        # Tentar carregar ícone, mas não crítico
        try:
            icon_path = "assets/icons/app.ico"
            if os.path.exists(icon_path):
                self.qt_app.setWindowIcon(QIcon(icon_path))
        except:
            pass  # Ícone não é crítico

    def initialize_components(self):
        """Inicialização segura dos componentes"""
        try:
            # Importar aqui para evitar dependências circulares
            from src.ui.main_window import MainWindow

            # Inicializar controladores básicos (simplificado por enquanto)
            spoofer_controller = self.create_dummy_controller()

            # Criar janela principal
            self.main_window = MainWindow(spoofer_controller)
            return True

        except Exception as e:
            print(f"Erro crítico na inicialização: {e}")
            self.show_error_message(str(e))
            return False

    def create_dummy_controller(self):
        """Cria controlador temporário para testes"""
        class DummyController:
            def __init__(self):
                self.status = "Ready"

        return DummyController()

    def show_error_message(self, error_details):
        """Mostra mensagem de erro amigável"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erro de Inicialização")
        msg.setText("Não foi possível iniciar o Lunar Spoofer")
        msg.setInformativeText(f"Detalhes: {error_details}")
        msg.setDetailedText(f"Traceback completo:\n{error_details}")
        msg.exec()

    def run(self):
        """Executa a aplicação de forma segura"""
        print("Iniciando Lunar Spoofer...")

        try:
            if self.initialize_components():
                self.main_window.show()
                print("Aplicação iniciada com sucesso")
                return self.qt_app.exec()
            else:
                print("Falha na inicialização")
                return 1

        except Exception as e:
            print(f"Erro fatal: {e}")
            self.show_error_message(str(e))
            return 1
