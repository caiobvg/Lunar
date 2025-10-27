# src/gui/main_window.py

import customtkinter as ctk
import threading
import time
import queue
from datetime import datetime
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cleaners.system_cleaner import SystemCleaner
from utils.hardware_reader import HardwareReader
from utils.logger import logger  # Import the unified logger
from .components.particles import ParticleSystem
from .components.buttons import AnimatedButton
from .components.progress import CircularProgress
from .components.toast import ToastNotification
from .components.stats import SystemStats


class MidnightSpooferGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Midnight Spoofer v2.0 - REAL SPOOFING")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.configure(fg_color="#0a0a1a")
        
        self.center_window()
        
        # Remove old queue system, use logger subscription
        self.log_queue = queue.Queue()
        self.cleaner = SystemCleaner()  # Remove realtime_callback
        
        # Register GUI as logger subscriber
        logger.add_subscriber(self.add_log_ui)
        
        # Inicializa o leitor de hardware
        try:
            self.hw_reader = HardwareReader()
        except Exception as e:
            print(f"Warning: Hardware reader initialization failed: {e}")
            self.hw_reader = None
        
        self.cleaning_in_progress = False
        self.sidebar_expanded = True
        self.current_theme = "purple"
        self.last_spoof_time = None
        
        self.toggle_states = {
            "HWID SPOOFER": False,
            "EFI SPOOFER": False,
            "RESET TPM": False,
            "NEW MAC": False,
            "ENABLE VPN": False
        }
        
        self.setup_ui()
        self.process_log_queue()  # Keep for backward compatibility during transition
        self.update_system_stats()
        
        # Use logger instead of direct UI calls
        logger.log_info("Midnight Spoofer Premium INITIALIZED", "SYSTEM")
        logger.log_real("REAL spoofing engine loaded", "SECURITY")
        logger.log_success("Discord/FiveM spoofing ready", "READY")
        logger.log_warning("Run as Administrator for full functionality", "INFO")
        
        # Move hardware initialization logs to after UI is fully set up
        if self.hw_reader:
            logger.log_info("Hardware reader initialized successfully", "HARDWARE")
        else:
            logger.log_warning("Hardware reader failed - using fallback data", "HARDWARE")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def add_log_realtime(self, message):
        """Deprecated - kept for backward compatibility during transition"""
        if self.log_queue:
            self.log_queue.put(message)

    def process_log_queue(self):
        """Deprecated - kept for backward compatibility"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.add_log_ui(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

    def add_log_ui(self, message):
        """Callback method for logger subscription - receives formatted messages"""
        # Check if logs_text exists before trying to use it
        if not hasattr(self, 'logs_text') or self.logs_text is None:
            print(f"LOG (UI not ready): {message}")
            return
            
        # Parse log level from message format: [TIME] [LEVEL] [CONTEXT] Message
        if "[ERROR]" in message:
            tag = "error"
        elif "[SUCCESS]" in message:
            tag = "success"
        elif "[WARNING]" in message:
            tag = "warning"
        elif "[SYSTEM]" in message or "[STATUS]" in message or "[INFO]" in message:
            tag = "system"
        elif "[REAL]" in message or "[HARDWARE]" in message or "[SECURITY]" in message:
            tag = "real"
        else:
            tag = "info"
        
        self.logs_text.configure(state="normal")
        self.logs_text.insert("end", f"{message}\n", tag)
        self.logs_text.see("end")
        self.logs_text.configure(state="disabled")

    def setup_ui(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.setup_sidebar()
        
        self.main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        self.setup_header()
        self.setup_dashboard()
        self.setup_log_highlighting()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root, fg_color="#1a1a2e", width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        logo_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(0, 30))
        
        logo_label = ctk.CTkLabel(logo_frame, text="🌙 MIDNIGHT", 
                                 font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                 text_color="#6b21ff")
        logo_label.pack(side="left")
        
        # Botão para atualizar hardware info
        refresh_hw_btn = ctk.CTkButton(
            logo_frame,
            text="🔄",
            command=self.refresh_hardware_info,
            width=40,
            height=40,
            fg_color="#2d1152",
            hover_color="#4a1c6d",
            font=ctk.CTkFont(size=16)
        )
        refresh_hw_btn.pack(side="right")
        
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🔧 Spoof Tools", self.show_spoof_tools),
            ("📜 History", self.show_history),
            ("⚙️ Settings", self.show_settings),
            ("ℹ️ About", self.show_about)
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(sidebar_content, text=text, command=command,
                               fg_color="transparent", hover_color="#2d1152",
                               anchor="w", height=45,
                               font=ctk.CTkFont(size=14))
            btn.pack(fill="x", pady=5)
        
        theme_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", pady=20)
        
        ctk.CTkLabel(theme_frame, text="THEME", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        theme_options = ctk.CTkSegmentedButton(theme_frame, values=["Purple", "Cyan", "Red"],
                                              command=self.switch_theme)
        theme_options.pack(fill="x", pady=5)
        theme_options.set("Purple")

    def setup_header(self):
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent", height=120)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.cpu_card = self.create_stat_card(header_frame, "CPU", "0%", 0, "#6b21ff")
        self.cpu_card.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.memory_card = self.create_stat_card(header_frame, "Memory", "0%", 1, "#00ff88")
        self.memory_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.disk_card = self.create_stat_card(header_frame, "Disk", "0%", 2, "#ffaa00")
        self.disk_card.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.status_card = self.create_status_card(header_frame)
        self.status_card.grid(row=0, column=3, padx=(10, 0), sticky="ew")

    def create_stat_card(self, parent, title, value, column, color):
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=15)
        
        title_label = ctk.CTkLabel(card, text=title, text_color="#b0b0ff",
                                  font=ctk.CTkFont(size=12))
        title_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        value_label = ctk.CTkLabel(card, text=value, text_color="white",
                                  font=ctk.CTkFont(size=18, weight="bold"))
        value_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        progress = ctk.CTkProgressBar(card, height=4, fg_color="#1a1a2e",
                                     progress_color=color)
        progress.pack(fill="x", padx=15, pady=(0, 10))
        progress.set(0)
        
        return card

    def create_status_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=15)
        
        title_label = ctk.CTkLabel(card, text="STATUS", text_color="#b0b0ff",
                                  font=ctk.CTkFont(size=12))
        title_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.status_dot = ctk.CTkLabel(content_frame, text="●", text_color="#00ff88",
                                      font=ctk.CTkFont(size=20))
        self.status_dot.pack(side="left", padx=(0, 10))
        
        self.status_text = ctk.CTkLabel(content_frame, text="System Ready", text_color="white",
                                       font=ctk.CTkFont(size=14, weight="bold"))
        self.status_text.pack(side="left", fill="both", expand=True)
        
        return card

    def setup_dashboard(self):
        content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        progress_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        progress_frame.pack(side="left", padx=(0, 20))
        
        self.circular_progress = CircularProgress(progress_frame, size=200)
        self.circular_progress.pack(pady=20)
        
        self.spoof_button = AnimatedButton(
            progress_frame,
            text="🚀 START SPOOFING",
            command=self.start_spoofing_sequence,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            height=50,
            width=200,
            fg_color="#2d1152",
            hover_color="#4a1c6d",
            text_color="#ffffff",
            corner_radius=25,
            border_width=3,
            border_color="#6b21ff"
        )
        self.spoof_button.pack(pady=(0, 20))
        
        # Container principal dividido em dois containers separados
        self.modules_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        self.modules_container.pack(side="right", fill="both", expand=True)
        
        # Configurar grid com duas colunas de tamanhos iguais
        self.modules_container.grid_columnconfigure(0, weight=1)
        self.modules_container.grid_columnconfigure(1, weight=1)
        self.modules_container.grid_rowconfigure(0, weight=1)
        
        # Criar dois containers separados com bordas distintas
        self.setup_spoofing_modules()
        self.setup_controls()
        
        # Create logs area
        self.setup_logs_area(content_frame)

    def setup_spoofing_modules(self):
        """Configura a seção esquerda - Spoofing Modules"""
        # Container principal para Spoofing Modules
        self.spoofing_frame = ctk.CTkFrame(
            self.modules_container, 
            fg_color="#1a1a2e", 
            corner_radius=15,
            height=280
        )
        self.spoofing_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.spoofing_frame.grid_propagate(False)
        
        # Título da seção
        spoofing_title = ctk.CTkLabel(
            self.spoofing_frame,
            text="🔧 SPOOFING MODULES",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#6b21ff"
        )
        spoofing_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Container para o conteúdo
        spoofing_content = ctk.CTkFrame(self.spoofing_frame, fg_color="transparent")
        spoofing_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Obtém dados REAIS do hardware
        if self.hw_reader:
            try:
                hw_data = self.hw_reader.get_all_hardware_ids()
            except Exception as e:
                hw_data = {
                    'disk_c': 'N/A',
                    'disk_d': 'N/A',
                    'motherboard': 'N/A',
                    'smbios_uuid': 'N/A',
                    'chassis': 'N/A',
                    'bios': 'N/A',
                    'cpu': 'N/A',
                    'mac': 'N/A'
                }
        else:
            hw_data = {
                'disk_c': 'N/A',
                'disk_d': 'N/A',
                'motherboard': 'N/A',
                'smbios_uuid': 'N/A',
                'chassis': 'N/A',
                'bios': 'N/A',
                'cpu': 'N/A',
                'mac': 'N/A'
            }
        
        # Mapeamento dos dados reais
        hardware_data = [
            ("Disk C:", hw_data.get('disk_c', 'N/A')),
            ("Disk D:", hw_data.get('disk_d', 'N/A')),
            ("Motherboard:", hw_data.get('motherboard', 'N/A')),
            ("Chassis:", hw_data.get('chassis', 'N/A')),
            ("Bios:", hw_data.get('bios', 'N/A')),
            ("Cpu:", hw_data.get('cpu', 'N/A')),
            ("Mac:", hw_data.get('mac', 'N/A')),
            ("Smbios UUID:", hw_data.get('smbios_uuid', 'N/A'))
        ]
        
        self.hardware_labels = {}
        for label_text, value in hardware_data:
            frame = ctk.CTkFrame(spoofing_content, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            
            label = ctk.CTkLabel(frame, text=label_text, text_color="#b0b0ff",
                               font=ctk.CTkFont(size=11))
            label.pack(side="left")
            
            # Trunca valores muito longos para caber na interface
            display_value = value if len(str(value)) <= 25 else str(value)[:22] + "..."
            
            value_label = ctk.CTkLabel(frame, text=display_value, text_color="#ffffff",
                                     font=ctk.CTkFont(size=11, weight="bold"))
            value_label.pack(side="left", padx=(5, 0))
            
            self.hardware_labels[label_text] = value_label

    def setup_controls(self):
        """Configura a seção direita - Controls"""
        # Container principal para Controls
        self.controls_frame = ctk.CTkFrame(
            self.modules_container, 
            fg_color="#1a1a2e", 
            corner_radius=15,
            height=280
        )
        self.controls_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.controls_frame.grid_propagate(False)
        
        # Título da seção
        controls_title = ctk.CTkLabel(
            self.controls_frame,
            text="⚙️ CONTROLS",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#6b21ff"
        )
        controls_title.pack(anchor="w", padx=20, pady=(20, 15))
        
        # Container para o conteúdo
        controls_content = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        controls_content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        toggle_options = [
            "HWID SPOOFER",
            "EFI SPOOFER", 
            "RESET TPM",
            "NEW MAC",
            "ENABLE VPN"
        ]
        
        self.toggle_switches = {}
        for option in toggle_options:
            self.create_toggle_switch(controls_content, option)

    def refresh_hardware_info(self):
        """Atualiza as informações de hardware na interface"""
        if not self.hw_reader:
            logger.log_error("Hardware reader not available", "HARDWARE")
            self.show_toast("Hardware reader unavailable", "error")
            return
        
        try:
            logger.log_info("Refreshing hardware information...", "HARDWARE")
            hw_data = self.hw_reader.get_all_hardware_ids()
            
            # Atualiza os labels
            hardware_mapping = {
                "Disk C:": hw_data.get('disk_c', 'N/A'),
                "Disk D:": hw_data.get('disk_d', 'N/A'),
                "Motherboard:": hw_data.get('motherboard', 'N/A'),
                "Chassis:": hw_data.get('chassis', 'N/A'),
                "Bios:": hw_data.get('bios', 'N/A'),
                "Cpu:": hw_data.get('cpu', 'N/A'),
                "Mac:": hw_data.get('mac', 'N/A'),
                "Smbios UUID:": hw_data.get('smbios_uuid', 'N/A')
            }
            
            for key, value in hardware_mapping.items():
                if key in self.hardware_labels:
                    display_value = value if len(str(value)) <= 25 else str(value)[:22] + "..."
                    self.hardware_labels[key].configure(text=display_value)
            
            logger.log_success("Hardware info refreshed successfully", "HARDWARE")
            self.show_toast("Hardware info updated", "success")
            
        except Exception as e:
            logger.log_error(f"Failed to refresh hardware: {str(e)}", "HARDWARE")
            self.show_toast("Hardware refresh failed", "error")

    def create_toggle_switch(self, parent, option):
        switch_frame = ctk.CTkFrame(parent, fg_color="transparent")
        switch_frame.pack(fill="x", pady=6)
        
        switch_frame.grid_columnconfigure(0, weight=1)
        switch_frame.grid_columnconfigure(1, weight=0)
        
        label = ctk.CTkLabel(switch_frame, text=option, text_color="#b0b0ff",
                           font=ctk.CTkFont(size=12))
        label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        switch = ctk.CTkSwitch(
            switch_frame,
            text="",
            width=45,
            height=20,
            switch_width=35,
            switch_height=16,
            corner_radius=8,
            border_width=1,
            button_color="#ffffff",
            button_hover_color="#f0f0f0",
            fg_color="#3a3a3a",
            progress_color="#6b21ff",
            border_color="#555555",
            command=lambda s=option: self.on_toggle_changed(s)
        )
        switch.grid(row=0, column=1, sticky="e", padx=(0, 5))
        
        self.toggle_switches[option] = switch

    def on_toggle_changed(self, option):
        new_state = self.toggle_switches[option].get()
        self.toggle_states[option] = new_state
        
        state_text = "ENABLED" if new_state else "DISABLED"
        logger.log_info(f"{option}: {state_text}", "CONTROL")
        
        if new_state:
            self.show_toast(f"{option} activated", "success")
        else:
            self.show_toast(f"{option} deactivated", "info")

    def setup_logs_area(self, parent):
        logs_container = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=15)
        logs_container.grid(row=1, column=0, sticky="nsew")
        logs_container.grid_columnconfigure(0, weight=1)
        logs_container.grid_rowconfigure(1, weight=1)
        
        logs_header = ctk.CTkFrame(logs_container, fg_color="transparent")
        logs_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 10))
        logs_header.grid_columnconfigure(0, weight=1)
        
        logs_title = ctk.CTkLabel(
            logs_header,
            text="📋 EXECUTION LOG - REAL TIME MONITORING",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#ffffff"
        )
        logs_title.grid(row=0, column=0, sticky="w")
        
        controls_frame = ctk.CTkFrame(logs_header, fg_color="transparent")
        controls_frame.grid(row=0, column=1, sticky="e")
        
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="🗑️ Clear",
            command=self.clear_logs,
            width=80,
            height=30,
            fg_color="#2d1152",
            hover_color="#4a1c6d"
        )
        clear_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            controls_frame,
            text="💾 Export",
            command=self.export_logs,
            width=80,
            height=30,
            fg_color="#2d1152",
            hover_color="#4a1c6d"
        )
        export_btn.pack(side="left", padx=5)
        
        text_frame = ctk.CTkFrame(logs_container, fg_color="transparent")
        text_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.logs_text = ctk.CTkTextbox(
            text_frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            fg_color="#0f0f23",
            text_color="#e0e0ff",
            border_width=2,
            border_color="#2d1152",
            corner_radius=10
        )
        self.logs_text.grid(row=0, column=0, sticky="nsew")

    def setup_log_highlighting(self):
        self.logs_text.tag_config("error", foreground="#ff4444")
        self.logs_text.tag_config("success", foreground="#00ff88")
        self.logs_text.tag_config("warning", foreground="#ffaa00")
        self.logs_text.tag_config("system", foreground="#6b21ff")
        self.logs_text.tag_config("real", foreground="#b0b0ff")
        self.logs_text.tag_config("info", foreground="#e0e0ff")

    def update_system_stats(self):
        try:
            cpu_usage = SystemStats.get_cpu_usage()
            memory_usage = SystemStats.get_memory_usage()
            disk_usage = SystemStats.get_disk_usage()
            
            self.update_stat_card(self.cpu_card, f"{cpu_usage:.1f}%", cpu_usage/100)
            self.update_stat_card(self.memory_card, f"{memory_usage:.1f}%", memory_usage/100)
            self.update_stat_card(self.disk_card, f"{disk_usage:.1f}%", disk_usage/100)
            
        except Exception as e:
            logger.log_error(f"Error updating stats: {e}", "SYSTEM")
        
        self.root.after(2000, self.update_system_stats)

    def update_stat_card(self, card, value, progress):
        for widget in card.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                if widget.cget("text").isdigit() or "%" in widget.cget("text"):
                    widget.configure(text=value)
            elif isinstance(widget, ctk.CTkProgressBar):
                widget.set(progress)

    def update_status(self, message, is_error=False, is_success=False):
        if is_error:
            dot_color = "#ff4444"
        elif is_success:
            dot_color = "#00ff88"
        else:
            dot_color = "#ffaa00"
            
        self.status_dot.configure(text_color=dot_color)
        self.status_text.configure(text=message)

    def show_toast(self, message, toast_type="info"):
        ToastNotification(self.root, message, toast_type)

    def switch_theme(self, theme):
        self.current_theme = theme.lower()
        self.show_toast(f"Theme switched to {theme}", "info")

    def start_spoofing_sequence(self):
        if self.cleaning_in_progress:
            return
        
        from tkinter import messagebox
            
        confirm = messagebox.askyesno(
            "🚨 CONFIRM REAL SPOOFING",
            "⚠️  WARNING: This will PERFORM REAL SYSTEM MODIFICATIONS:\n\n"
            "• TERMINATE Discord, FiveM, Steam processes\n" 
            "• RENAME Discord RPC folders to break tracking\n"
            "• CLEAN FiveM cache and registry traces\n"
            "• RESET network configurations\n"
            "• DELETE temporary system files\n\n"
            "✅ This is NOT a simulation - real changes will be made!\n\n"
            "Continue with REAL spoofing protocol?",
            icon='warning'
        )
        
        if not confirm:
            logger.log_warning("Spoofing cancelled by user", "USER")
            return
            
        self.start_spoofing()

    def start_spoofing(self):
        self.cleaning_in_progress = True
        self.spoof_button.configure(state="disabled", text="🔄 REAL SPOOFING...")
        self.spoof_button.start_pulse()
        self.clear_logs()
        self.update_status("Executing REAL spoofing protocol")
        self.circular_progress.set_progress(0)
        
        enabled_modules = [module for module, state in self.toggle_states.items() if state]
        if enabled_modules:
            logger.log_info(f"Active: {', '.join(enabled_modules)}", "MODULES")
        
        self.show_toast("Starting REAL spoofing...", "info")
        
        thread = threading.Thread(target=self.execute_spoofing)
        thread.daemon = True
        thread.start()

    def execute_spoofing(self):
        try:
            logger.log_real("🚀 INITIATING REAL SPOOFING PROTOCOL", "REAL")
            logger.log_real("This will actually modify system files", "REAL")
            logger.log_real("=" * 50, "REAL")
            
            # Mostra valores ANTES do spoof
            if self.hw_reader:
                logger.log_info("Current Hardware IDs (BEFORE):", "HARDWARE")
                try:
                    hw_before = self.hw_reader.get_all_hardware_ids()
                    for key, value in hw_before.items():
                        display_value = value if len(str(value)) <= 40 else str(value)[:37] + "..."
                        logger.log_info(f"{key}: {display_value}", "HARDWARE")
                except Exception as e:
                    logger.log_warning(f"Could not read hardware before spoof: {str(e)}", "HARDWARE")
            
            success = self.cleaner.execute_real_spoofing()
            
            if success:
                self.last_spoof_time = datetime.now()
                
                # Atualiza display após spoof
                if self.hw_reader:
                    logger.log_info("Refreshing hardware display...", "HARDWARE")
                    try:
                        self.refresh_hardware_info()
                    except Exception as e:
                        logger.log_warning(f"Could not refresh hardware display: {str(e)}", "HARDWARE")
                
                self.circular_progress.set_progress(100)
                self.update_status("REAL spoofing completed!", is_success=True)
                self.show_toast("Discord successfully spoofed!", "success")
                logger.log_success("✅ REAL SPOOFING COMPLETED!", "SUCCESS")
                logger.log_success("Discord RPC has been modified", "SECURITY")
                logger.log_success("FiveM cache has been cleared", "SECURITY")
            else:
                self.circular_progress.set_progress(75)
                self.update_status("Some operations failed", is_error=True)
                self.show_toast("Some spoofing operations failed", "warning")
                logger.log_warning("⚠️  Some spoofing operations may have failed", "WARNING")
            
        except Exception as e:
            logger.log_error(f"Spoofing failed completely: {str(e)}", "CRITICAL")
            self.update_status("Critical failure", is_error=True)
            self.show_toast("Spoofing failed critically!", "error")
        finally:
            self.cleaning_in_progress = False
            self.spoof_button.configure(state="normal", text="🚀 START SPOOFING")
            self.spoof_button.stop_pulse()

    def clear_logs(self):
        self.logs_text.configure(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.configure(state="disabled")
        logger.log_info("Log cleared", "SYSTEM")
        self.show_toast("Logs cleared", "info")

    def export_logs(self):
        try:
            filename = f"midnight_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.logs_text.get("1.0", "end"))
            self.show_toast(f"Logs exported to {filename}", "success")
            logger.log_info(f"Logs exported to {filename}", "SYSTEM")
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}", "error")
            logger.log_error(f"Export failed: {str(e)}", "ERROR")

    def show_dashboard(self):
        self.show_toast("Dashboard loaded", "info")

    def show_spoof_tools(self):
        self.show_toast("Spoof tools panel", "info")

    def show_history(self):
        self.show_toast("History panel", "info")

    def show_settings(self):
        self.show_toast("Settings panel", "info")

    def show_about(self):
        from tkinter import messagebox
        about_text = """
        Midnight Spoofer v2.0
        Advanced system identity protection
        
        • Real Discord RPC spoofing
        • FiveM cache cleaning
        • Network configuration reset
        • Registry sanitization
        • Real hardware ID detection
        
        ⚠️ Always run as Administrator
        for full functionality.
        
        📌 Educational purposes only
        """   
        messagebox.showinfo("About Midnight Spoofer", about_text)

    def run(self):
        self.root.mainloop()