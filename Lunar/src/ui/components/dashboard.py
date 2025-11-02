from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QGridLayout, QWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import psutil

from src.ui.components.switch import SwitchButton

class Dashboard(QFrame):
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
        """Configura dashboard com hardware stats acima do spoofing"""
        self.setObjectName("dashboard")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(25)

        # Painel de hardware (novo)
        hardware_panel = self.create_hardware_panel()
        main_layout.addWidget(hardware_panel)

        # Área de conteúdo principal
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)

    def create_content_area(self):
        """Cria área de conteúdo principal"""
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")

        layout = QHBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)

        # Painel de ações principal (esquerda)
        action_panel = self.create_action_panel()
        layout.addWidget(action_panel)

        # Painel de módulos compacto (direita)
        modules_panel = self.create_compact_modules_panel()
        layout.addWidget(modules_panel)

        return content_frame

    def create_hardware_panel(self):
        """Cria painel de informações de hardware"""
        hardware_frame = QFrame()
        hardware_frame.setObjectName("hardwarePanel")
        hardware_frame.setFixedHeight(100)

        layout = QHBoxLayout(hardware_frame)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(25)

        # Stats de hardware
        self.cpu_stat = self.create_hardware_stat("CPU", "0%", "#50E3C2")
        self.memory_stat = self.create_hardware_stat("MEMORY", "0%", "#4A90E2")
        self.disk_stat = self.create_hardware_stat("DISK", "0%", "#B8E986")
        self.status_stat = self.create_hardware_stat("STATUS", "READY", "#FF6B6B")

        layout.addWidget(self.cpu_stat)
        layout.addWidget(self.memory_stat)
        layout.addWidget(self.disk_stat)
        layout.addWidget(self.status_stat)
        layout.addStretch(1)

        return hardware_frame

    def create_hardware_stat(self, title, value, color):
        """Cria widget individual de stat de hardware"""
        widget = QFrame()
        widget.setObjectName("hardwareStat")
        widget.setFixedSize(120, 70)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("hardwareTitle")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("hardwareValue")
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        
        # Aplicar cor diretamente via estilo
        value_label.setStyleSheet(f"color: {color}; background: transparent;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return widget

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

        # Título
        title_label = QLabel("SYSTEM SECURITY")
        title_label.setObjectName("sectionTitle")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

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

        button_layout.addWidget(title_label)
        button_layout.addWidget(self.spoof_button)
        button_layout.addWidget(self.spoof_status)

        layout.addWidget(button_container)
        layout.addStretch(1)

        return action_frame

    def create_compact_modules_panel(self):
        """Cria painel de módulos compacto com switches"""
        modules_frame = QFrame()
        modules_frame.setObjectName("modulesPanel")
        modules_frame.setFixedWidth(300)

        layout = QVBoxLayout(modules_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title = QLabel("SECURITY MODULES")
        title.setObjectName("modulesTitle")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))

        layout.addWidget(title)

        # Container dos switches
        switches_container = QWidget()
        switches_layout = QVBoxLayout(switches_container)
        switches_layout.setContentsMargins(0, 0, 0, 0)
        switches_layout.setSpacing(10)

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
        row_widget = QFrame()
        row_widget.setObjectName(f"switchRow_{module_id}")
        row_widget.setFixedHeight(35)

        layout = QHBoxLayout(row_widget)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(15)

        # Nome do módulo
        name_label = QLabel(name)
        name_label.setObjectName("moduleName")
        name_label.setFont(QFont("Segoe UI", 11))

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

    def setup_timers(self):
        """Configura timers para atualização em tempo real"""
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_hardware_stats)
        self.stats_timer.start(2000)
        self.update_hardware_stats()

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

    def update_hardware_stats(self):
        """Atualiza as estatísticas de hardware"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_stat.findChild(QLabel, "hardwareValue").setText(f"{cpu_percent:.0f}%")

            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_stat.findChild(QLabel, "hardwareValue").setText(f"{memory_percent:.0f}%")

            # Disco
            try:
                disk = psutil.disk_usage('C:')
                disk_percent = disk.percent
                self.disk_stat.findChild(QLabel, "hardwareValue").setText(f"{disk_percent:.0f}%")
            except:
                self.disk_stat.findChild(QLabel, "hardwareValue").setText("N/A")

            # Status baseado na CPU
            if cpu_percent > 80:
                self.status_stat.findChild(QLabel, "hardwareValue").setText("HIGH LOAD")
                self.status_stat.findChild(QLabel, "hardwareValue").setStyleSheet("color: #FF6B6B;")
            elif cpu_percent > 50:
                self.status_stat.findChild(QLabel, "hardwareValue").setText("MODERATE")
                self.status_stat.findChild(QLabel, "hardwareValue").setStyleSheet("color: #FFA726;")
            else:
                self.status_stat.findChild(QLabel, "hardwareValue").setText("OPTIMAL")
                self.status_stat.findChild(QLabel, "hardwareValue").setStyleSheet("color: #B8E986;")

        except Exception as e:
            print(f"Hardware stats update error: {e}")
