from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QFrame,
                              QVBoxLayout, QPushButton)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap, QPainter
import psutil

class HeaderBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.setup_ui()
        self.setup_timers()

    def setup_ui(self):
        self.setObjectName("headerBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 15, 30, 15)
        layout.setSpacing(25)

        # Logo e título à esquerda
        logo_section = self.create_logo_section()
        layout.addWidget(logo_section)

        # Stats no centro
        stats_section = self.create_stats_section()
        layout.addWidget(stats_section)

        # Botão de ação à direita
        action_section = self.create_action_section()
        layout.addWidget(action_section)

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

    def create_stats_section(self):
        section = QFrame()
        section.setObjectName("statsSection")
        layout = QHBoxLayout(section)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(25)

        # CPU
        self.cpu_stat = self.create_stat_widget("CPU", "0%", "#50E3C2")
        layout.addWidget(self.cpu_stat)

        # Memory
        self.memory_stat = self.create_stat_widget("MEMORY", "0%", "#4A90E2")
        layout.addWidget(self.memory_stat)

        # Disk
        self.disk_stat = self.create_stat_widget("DISK", "0%", "#B8E986")
        layout.addWidget(self.disk_stat)

        # Status
        self.status_stat = self.create_stat_widget("STATUS", "READY", "#FF6B6B")
        layout.addWidget(self.status_stat)

        return section

    def create_stat_widget(self, title, value, color):
        widget = QFrame()
        widget.setObjectName("statWidget")
        widget.setFixedSize(90, 60)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setFont(QFont("Segoe UI", 9, QFont.Medium))
        title_label.setAlignment(Qt.AlignCenter)

        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return widget

    def create_action_section(self):
        section = QFrame()
        section.setObjectName("actionSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.launch_button = QPushButton("LAUNCH SECURITY")
        self.launch_button.setObjectName("launchButton")
        self.launch_button.setFixedSize(160, 35)
        self.launch_button.setCursor(Qt.PointingHandCursor)

        version_label = QLabel("Lunar Client 1.0.8")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(QFont("Segoe UI", 9))

        layout.addWidget(self.launch_button)
        layout.addWidget(version_label)

        return section

    def setup_timers(self):
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_system_stats)
        self.stats_timer.start(2000)
        self.update_system_stats()

    def update_system_stats(self):
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.cpu_stat.findChild(QLabel, "statValue").setText(f"{cpu_percent:.0f}%")

            # Memória
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_stat.findChild(QLabel, "statValue").setText(f"{memory_percent:.0f}%")

            # Disco
            try:
                disk = psutil.disk_usage('C:')
                disk_percent = disk.percent
                self.disk_stat.findChild(QLabel, "statValue").setText(f"{disk_percent:.0f}%")
            except:
                self.disk_stat.findChild(QLabel, "statValue").setText("N/A")

        except Exception as e:
            print(f"Stats update error: {e}")
