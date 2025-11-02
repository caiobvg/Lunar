from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QFrame, QPushButton, QProgressBar, QGridLayout)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import psutil

from src.ui.components.switch import SwitchButton

class Dashboard(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.switch_states = {
            "mac": False,
            "guid": False,
            "hwid": False
        }
        self.setup_ui()
        self.setup_timers()

    def setup_ui(self):
        """Configura dashboard com layout compacto"""
        self.setObjectName("dashboard")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Header de estatísticas
        stats_header = self.create_stats_header()
        main_layout.addWidget(stats_header)

        # Área de conteúdo
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)

    def create_stats_header(self):
        """Cria header de estatísticas elegante"""
        header_frame = QFrame()
        header_frame.setObjectName("statsHeader")
        header_frame.setFixedHeight(100)

        layout = QGridLayout(header_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(0)

        # Cartões de sistema
        self.cpu_card = self.create_stat_card("CPU", "0%", 0, "#ffffff")
        self.memory_card = self.create_stat_card("MEMORY", "0%", 0, "#f0f0f0")
        self.disk_card = self.create_stat_card("DISK", "0%", 0, "#e0e0e0")
        self.status_card = self.create_status_card()

        layout.addWidget(self.cpu_card, 0, 0)
        layout.addWidget(self.memory_card, 0, 1)
        layout.addWidget(self.disk_card, 0, 2)
        layout.addWidget(self.status_card, 0, 3)

        return header_frame

    def create_stat_card(self, title, value, progress, color):
        """Cria cartão de estatística minimalista"""
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(80)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)

        # Título
        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 9))

        # Valor
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 14, QFont.Bold))

        # Barra de progresso sutil
        progress_bar = QProgressBar()
        progress_bar.setObjectName("statProgress")
        progress_bar.setValue(progress)
        progress_bar.setFixedHeight(3)
        progress_bar.setTextVisible(False)

        # Aplicar cor
        progress_bar.setProperty("progressColor", color)
        value_label.setProperty("valueColor", color)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(progress_bar)

        return card

    def create_status_card(self):
        """Cria cartão de status elegante"""
        card = QFrame()
        card.setObjectName("statusCard")
        card.setFixedHeight(80)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(6)

        # Título
        title_label = QLabel("STATUS")
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 9))

        # Conteúdo do status
        status_content = QWidget()
        status_layout = QHBoxLayout(status_content)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(8)

        # Indicador de status
        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("statusDot")
        self.status_dot.setFont(QFont("Segoe UI", 12))

        # Texto do status
        self.status_text = QLabel("System Ready")
        self.status_text.setObjectName("statusText")
        self.status_text.setFont(QFont("Segoe UI", 11, QFont.Bold))

        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch(1)

        layout.addWidget(title_label)
        layout.addWidget(status_content)

        return card

    def create_content_area(self):
        """Cria área de conteúdo principal"""
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")

        layout = QHBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Painel de ações principal (esquerda)
        action_panel = self.create_action_panel()
        layout.addWidget(action_panel)

        # Painel de módulos compacto (direita)
        modules_panel = self.create_compact_modules_panel()
        layout.addWidget(modules_panel)

        return content_frame

    def create_action_panel(self):
        """Cria painel de ações principal"""
        action_frame = QFrame()
        action_frame.setObjectName("actionPanel")

        layout = QVBoxLayout(action_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # Container do botão principal
        button_container = QFrame()
        button_container.setObjectName("buttonContainer")
        button_container.setFixedHeight(180)

        button_layout = QVBoxLayout(button_container)
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(15)

        # Botão de spoofing principal
        self.spoof_button = QPushButton("START SPOOFING")
        self.spoof_button.setObjectName("mainSpoofButton")
        self.spoof_button.setCursor(Qt.PointingHandCursor)
        self.spoof_button.setFixedHeight(52)
        self.spoof_button.clicked.connect(self.on_spoof_button_click)

        # Status do spoofing
        self.spoof_status = QLabel("System ready for spoofing protocol")
        self.spoof_status.setObjectName("spoofStatus")
        self.spoof_status.setAlignment(Qt.AlignCenter)
        self.spoof_status.setWordWrap(True)

        button_layout.addWidget(self.spoof_button)
        button_layout.addWidget(self.spoof_status)

        layout.addWidget(button_container)
        layout.addStretch(1)

        return action_frame

    def create_compact_modules_panel(self):
        """Cria painel de módulos ultra compacto com switches"""
        modules_frame = QFrame()
        modules_frame.setObjectName("modulesPanel")
        modules_frame.setFixedWidth(280)  # Largura fixa para compactação
        modules_frame.setFixedHeight(160)  # Altura compacta

        layout = QVBoxLayout(modules_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Título
        title = QLabel("SPOOFING MODULES")
        title.setObjectName("modulesTitle")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))

        layout.addWidget(title)

        # Container dos switches
        switches_container = QWidget()
        switches_layout = QVBoxLayout(switches_container)
        switches_layout.setContentsMargins(0, 0, 0, 0)
        switches_layout.setSpacing(8)

        # Módulos com switches
        modules_data = [
            ("MAC Address Spoofing", "mac"),
            ("GUID Spoofing", "guid"),
            ("HWID Spoofing", "hwid")
        ]

        self.module_switches = {}

        for module_name, module_id in modules_data:
            switch_widget = self.create_switch_row(module_name, module_id)
            switches_layout.addWidget(switch_widget)
            self.module_switches[module_id] = switch_widget.findChild(SwitchButton)

        layout.addWidget(switches_container)
        layout.addStretch(1)

        return modules_frame

    def create_switch_row(self, name, module_id):
        """Cria uma linha compacta com switch"""
        row_widget = QWidget()
        row_widget.setObjectName(f"switchRow_{module_id}")
        row_widget.setFixedHeight(32)

        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(10)

        # Nome do módulo
        name_label = QLabel(name)
        name_label.setObjectName("moduleName")
        name_label.setFont(QFont("Segoe UI", 10))

        # Switch
        switch = SwitchButton()
        switch.setObjectName(f"moduleSwitch_{module_id}")
        switch.toggled.connect(lambda checked, mid=module_id: self.on_module_toggled(mid, checked))

        layout.addWidget(name_label)
        layout.addStretch(1)
        layout.addWidget(switch)

        return row_widget

    def on_module_toggled(self, module_id, checked):
        """Handler para toggle dos módulos"""
        self.switch_states[module_id] = checked
        status = "ENABLED" if checked else "DISABLED"
        print(f"Module {module_id}: {status}")

        # Atualizar interface baseada no estado
        self.update_module_states()

    def update_module_states(self):
        """Atualiza estados visuais dos módulos"""
        # Aqui você pode adicionar lógica para atualizar a interface
        # baseada nos estados dos switches
        enabled_count = sum(1 for state in self.switch_states.values() if state)
        self.status_text.setText(f"{enabled_count} modules enabled")

    def setup_timers(self):
        """Configura timers para atualização em tempo real"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(2000)
        self.update_system_stats()

    def update_system_stats(self):
        """Atualiza estatísticas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.update_stat_card(self.cpu_card, f"{cpu_percent:.1f}%", int(cpu_percent))

            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.update_stat_card(self.memory_card, f"{memory_percent:.1f}%", int(memory_percent))

            # Disco
            try:
                disk = psutil.disk_usage('C:')
                disk_percent = disk.percent
                self.update_stat_card(self.disk_card, f"{disk_percent:.1f}%", int(disk_percent))
            except:
                self.update_stat_card(self.disk_card, "N/A", 0)

        except Exception as e:
            print(f"Stats update error: {e}")

    def update_stat_card(self, card, value, progress):
        """Atualiza cartão de estatística"""
        value_label = card.findChild(QLabel, "statValue")
        progress_bar = card.findChild(QProgressBar)

        if value_label:
            value_label.setText(value)
        if progress_bar:
            progress_bar.setValue(progress)

    def on_spoof_button_click(self):
        """Handler do botão de spoofing"""
        # Coletar estados dos switches
        enabled_modules = [mid for mid, state in self.switch_states.items() if state]

        if not enabled_modules:
            self.spoof_status.setText("No modules enabled for spoofing")
            return

        self.spoof_button.setText("PROCESSING...")
        self.spoof_button.setEnabled(False)
        self.spoof_status.setText(f"Executing: {', '.join(enabled_modules)}")

        # Simular processamento
        QTimer.singleShot(3000, self.reset_spoof_button)

    def reset_spoof_button(self):
        """Reseta botão após processamento"""
        self.spoof_button.setText("START SPOOFING")
        self.spoof_button.setEnabled(True)
        self.spoof_status.setText("Security protocol completed")

        QTimer.singleShot(2000, lambda: self.spoof_status.setText("System ready for spoofing protocol"))
