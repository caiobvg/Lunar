from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QGridLayout, QWidget)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
# import psutil # REMOVED (now in hardware_reader)

# NEW IMPORTS
from src.utils.hardware_reader import HardwareReader
from src.ui.components.hardware_graphs import MiniGraphWidget

from src.ui.components.switch import SwitchButton

# NOVO IMPORT
from src.ui.components.progress_button import ProgressButton

# NEW: Define a ceiling for the DISK graph (ex: 100 MB/s = 100%)
DISK_GRAPH_MAX_MB_S = 100.0

class Dashboard(QFrame):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.switch_states = {
            "mac": False,
            "guid": False,
            "hwid": False
        }

        # Instantiate the reader
        self.hw_reader = HardwareReader()

        self.setup_ui()
        self.setup_timers()

    def setup_ui(self):
        """Configura dashboard com hardware stats ACIMA e flutuante"""
        self.setObjectName("dashboard")

        # Layout principal REMOVIDO
        # main_layout = QVBoxLayout(self)
        # main_layout.setContentsMargins(30, 20, 30, 20)
        # main_layout.setSpacing(25)
        self.setLayout(None) # Define layout nulo para posicionamento manual

        # Painel de hardware (agora flutuante)
        self.hardware_panel = self.create_hardware_panel()
        self.hardware_panel.setParent(self) # Define o parent
        # main_layout.addWidget(hardware_panel) # REMOVIDO

        # Área de conteúdo principal
        self.content_area = self.create_content_area()
        self.content_area.setParent(self) # Define o parent
        # main_layout.addWidget(content_area) # REMOVIDO

    def resizeEvent(self, event):
        """Posiciona os painéis manualmente"""
        super().resizeEvent(event)
        w = self.width()
        h = self.height()

        panel_height = 60
        # ALTERADO DE 20 PARA 30 (para alinhar com os ícones do header)
        panel_margin_top = 30
        # ALTERADO DE 110 PARA 120 (para descer o conteúdo)
        content_margin_top = 120

        # Posiciona o painel de hardware no topo e centro
        if hasattr(self, 'hardware_panel'):
            panel_width = self.hardware_panel.width() # 600px fixo
            self.hardware_panel.setGeometry(
                30,  # Alinhado à esquerda com o conteúdo
                panel_margin_top,        # Margem do topo
                panel_width,
                panel_height
            )
            self.hardware_panel.raise_()

        # Posiciona a área de conteúdo abaixo do painel
        if hasattr(self, 'content_area'):
            self.content_area.setGeometry(
                30, # Margem esquerda
                content_margin_top,
                w - 60, # Margem esquerda/direita
                h - content_margin_top - 20 # Margem topo/baixo
            )

    def create_content_area(self):
        """Cria área de conteúdo principal"""
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")

        layout = QHBoxLayout(content_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(25)

        # Painel de ações principal (esquerda)
        action_panel = self.create_action_panel()
        layout.addWidget(action_panel, 0, Qt.AlignTop)

        # Painel de módulos compacto (direita)
        modules_panel = self.create_compact_modules_panel()
        layout.addWidget(modules_panel, 0, Qt.AlignTop)

        return content_frame

    def create_hardware_panel(self):
        """Cria painel de informações de hardware (Estilo Pill)"""
        hardware_frame = QFrame()
        # [ALTERADO] Novo objectName para o CSS
        hardware_frame.setObjectName("pillHardwarePanel")
        hardware_frame.setFixedHeight(60) # de 80 para 60
        hardware_frame.setFixedWidth(900) # de 600 para 900

        layout = QHBoxLayout(hardware_frame)
        layout.setContentsMargins(20, 7, 20, 3) # Margens (esquerda/direita 20)
        layout.setSpacing(10) # Espaçamento reduzido

        # Stats de hardware (com gráficos)
        self.cpu_stat = self.create_hardware_stat("CPU", "0%", "#50E3C2", show_graph=True)
        self.memory_stat = self.create_hardware_stat("MEMORY", "0%", "#4A90E2", show_graph=True)
        self.disk_stat = self.create_hardware_stat("DISK", "0 MB/s", "#B8E986", show_graph=True)
        self.status_stat = self.create_hardware_stat("STATUS", "READY", "#FF6B6B", show_graph=False)

        layout.addWidget(self.cpu_stat)
        layout.addStretch(1) # Espaçador
        layout.addWidget(self.memory_stat)
        layout.addStretch(1) # Espaçador
        layout.addWidget(self.disk_stat)
        layout.addStretch(1) # Espaçador
        layout.addWidget(self.status_stat)

        return hardware_frame

    def create_hardware_stat(self, title, value, color, show_graph=True):
        """Cria widget de stat (Texto + Gráfico Opcional)"""

        # Widget principal (Stat + Gráfico)
        main_widget = QFrame()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Widget de Texto (Título + Valor)
        text_widget = QFrame()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        text_layout.setAlignment(Qt.AlignCenter)
        text_widget.setFixedWidth(80) # Largura fixa para o texto

        title_label = QLabel(title)
        title_label.setObjectName("hardwareTitle")
        title_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        value_label = QLabel(value)
        value_label.setObjectName("hardwareValue")
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        value_label.setStyleSheet(f"color: {color}; background: transparent;")

        text_layout.addWidget(title_label)
        text_layout.addWidget(value_label)

        main_layout.addWidget(text_widget) # Adiciona texto à esquerda

        # Gráfico (Direita)
        if show_graph:
            graph_widget = MiniGraphWidget()
            graph_widget.set_color(color)
            main_layout.addWidget(graph_widget) # Adiciona gráfico à direita

            # Armazenar referência ao gráfico
            if title == "CPU":
                self.cpu_graph = graph_widget
            elif title == "MEMORY":
                self.memory_graph = graph_widget
            elif title == "DISK":
                self.disk_graph = graph_widget

            # (80px texto + 10px espaço + 100px gráfico)
            main_widget.setFixedSize(190, 50)
        else:
            # Se não houver gráfico, o tamanho é menor
            main_widget.setFixedSize(90, 50)

        return main_widget

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
        self.spoof_button = ProgressButton("START SPOOFING")
        self.spoof_button.setObjectName("mainSpoofButton")
        self.spoof_button.setCursor(Qt.PointingHandCursor)
        self.spoof_button.setFixedHeight(52)
        self.spoof_button.clicked.connect(self.on_spoof_button_click)
        # CONECTA O NOVO SINAL DE "FINALIZADO"
        self.spoof_button.simulation_finished.connect(self.reset_spoof_button)

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
        # layout.addStretch(1) # REMOVED - prevents vertical stretching

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
        # Atualização mais rápida para o gráfico
        self.stats_timer.start(1000) # 1 segundo
        # A primeira chamada deve ser do timer, após 1s.
        # self.update_hardware_stats()

    def on_spoof_button_click(self):
        """Handler do botão de spoofing"""
        # Coletar estados dos switches
        enabled_modules = [mid for mid, state in self.switch_states.items() if state]

        if not enabled_modules:
            self.spoof_status.setText("No modules enabled for spoofing")
            return

        self.spoof_status.setText(f"Executing: {', '.join(enabled_modules)}")

        # Inicia o botão no modo de carregamento e RODA a simulação
        self.spoof_button.start_loading(run_simulation=True)

    def reset_spoof_button(self):
        """Reseta botão após processamento"""
        # CHAMA A FUNÇÃO DE PARADA DO BOTÃO
        self.spoof_button.stop_loading()

        self.spoof_status.setText("Security protocol completed")
        QTimer.singleShot(2000, lambda: self.spoof_status.setText("System ready for spoofing protocol"))

    def update_hardware_stats(self):
        """Atualiza as estatísticas de hardware e os gráficos"""
        try:
            # Buscar dados do Reader
            cpu_percent = self.hw_reader.get_cpu_percent()
            memory_percent = self.hw_reader.get_memory_percent()
            disk_mbs = self.hw_reader.get_disk_mbs() # CHANGED

            # Atualizar Labels
            self.cpu_stat.findChild(QLabel, "hardwareValue").setText(f"{cpu_percent:.0f}%")
            self.memory_stat.findChild(QLabel, "hardwareValue").setText(f"{memory_percent:.0f}%")
            # CHANGED: Format the disk label as MB/s
            self.disk_stat.findChild(QLabel, "hardwareValue").setText(f"{disk_mbs:.0f} MB/s")

            # Atualizar Gráficos
            if hasattr(self, 'cpu_graph'):
                self.cpu_graph.add_data_point(cpu_percent)
            if hasattr(self, 'memory_graph'):
                self.memory_graph.add_data_point(memory_percent)
            if hasattr(self, 'disk_graph'):
                # CHANGED: Calculate the % for the graph
                disk_percent_for_graph = (disk_mbs / DISK_GRAPH_MAX_MB_S) * 100.0
                self.disk_graph.add_data_point(disk_percent_for_graph)

            # Atualizar Status
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
