# src/dashboard/dashboard.py

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
from utils.logger import logger
from spoofers.mac_spoofer.mac_spoofer import MACSpoofer
from spoofers.mac_spoofer.select_network import InterfaceSelectionDialog
from .components.particles import ParticleSystem
from .components.buttons import AnimatedButton
from .components.progress import CircularProgress
from .components.toast import ToastNotification
from .components.stats import SystemStats
from controllers.spoofer_controller import SpoofingController


class MidnightSpooferGUI:
    def __init__(self, spoofer_controller):
        self.root = ctk.CTk()
        self.root.title("Midnight Spoofer Beta")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.configure(fg_color="#0a0a1a")
        
        self.center_window()
        
        self.controller = spoofer_controller
        
        # Register GUI as logger subscriber
        logger.add_subscriber(self.add_log_ui)
        
        # Define and register UI callbacks with the controller
        ui_callbacks = {
            'on_start': self.handle_spoofing_start,
            'on_success': self.handle_spoofing_success,
            'on_failure': self.handle_spoofing_failure,
            'on_finish': self.handle_spoofing_finish,
        }
        self.controller.set_ui_callbacks(ui_callbacks)
        
        self.cleaning_in_progress = False
        self.sidebar_expanded = True
        self.current_theme = "purple"
        self.last_spoof_time = None
        
        self.toggle_states = {
            "MAC SPOOFING": False,
            "GUID SPOOFING": False,
            "HWID SPOOFER": False,
            "EFI SPOOFER": False,
            "RESET TPM": False,
            "ENABLE VPN": False
        }
        # Stored MAC selection (deferred until Start Spoofing)
        self.selected_interface = None
        self.selected_vendor = None
        self.selected_mac = None

        # Inicializar dicionário de frames das abas
        self.tab_frames = {}
        self.current_tab = "HARDWARE"

        self.setup_ui()
        self.update_system_stats()

        # Use logger instead of direct UI calls
        logger.log_info("Midnight Spoofer Premium INITIALIZED", "SYSTEM")
        logger.log_info("Spoofing engine loaded", "SECURITY")
        logger.log_success("Discord/FiveM spoofing ready", "READY")
        logger.log_warning("Run as Administrator for full functionality", "INFO")
        logger.log_info("MAC Spoofer module loaded", "MAC")

        # Move hardware initialization logs to after UI is fully set up
        if self.controller.hw_reader:
            logger.log_info("Hardware reader initialized successfully", "HARDWARE")
        else:
            logger.log_warning("Hardware reader failed - using fallback data", "HARDWARE")

        # Schedule initial data loading after UI is fully set up
        self.root.after(100, self.initial_data_load)

    def initial_data_load(self):
        """Load hardware and software data after UI initialization with retry logic"""
        try:
            logger.log_info("Starting initial data loading...", "SYSTEM")
            self.update_status("Loading system information...")

            # Check if hardware reader is available
            if not self.controller.hw_reader:
                logger.log_error("Hardware reader not available during initial load", "HARDWARE")
                self.update_status("Hardware reader unavailable", is_error=True)
                self.show_toast("Hardware reader unavailable", "error")
                return

            # Set loading states for all labels
            self._set_loading_states()

            # Attempt to load data with retry logic
            success = self._load_data_with_retry()

            if success:
                logger.log_success("Initial data loading completed", "SYSTEM")
                self.update_status("System information loaded", is_success=True)
                self.show_toast("System information loaded", "success")
            else:
                logger.log_error("Initial data loading failed after retries", "SYSTEM")
                self.update_status("Failed to load system information", is_error=True)
                self.show_toast("Failed to load system information", "error")

        except Exception as e:
            logger.log_error(f"Critical error in initial data loading: {str(e)}", "SYSTEM")
            self.update_status("Critical loading error", is_error=True)
            self.show_toast("Critical loading error", "error")

    def _set_loading_states(self):
        """Set all labels to loading state"""
        try:
            # Hardware loading states
            if hasattr(self, 'hardware_labels'):
                for label_text in self.hardware_labels:
                    if label_text in self.hardware_labels and self.hardware_labels[label_text].winfo_exists():
                        self.hardware_labels[label_text].configure(text="Loading...", text_color="#ffaa00")

            # Software loading states
            if hasattr(self, 'software_labels'):
                for label_text in self.software_labels:
                    if label_text in self.software_labels and self.software_labels[label_text].winfo_exists():
                        self.software_labels[label_text].configure(text="Loading...", text_color="#ffaa00")

        except Exception as e:
            logger.log_error(f"Error setting loading states: {str(e)}", "UI")

    def _load_data_with_retry(self, max_retries=3, delay=1000):
        """Load data with retry logic and timeout handling"""
        for attempt in range(max_retries):
            try:
                logger.log_info(f"Data loading attempt {attempt + 1}/{max_retries}", "SYSTEM")

                # Load hardware data
                hw_data = self.controller.hw_reader.get_formatted_hardware_data(self.controller.mac_spoofer)
                if hw_data:
                    hardware_mapping = {
                        "Disk C:": hw_data.get('disk_c', 'N/A'),
                        "Disk D:": hw_data.get('disk_d', 'N/A'),
                        "Motherboard:": hw_data.get('motherboard', 'N/A'),
                        "Chassis:": hw_data.get('chassis', 'N/A'),
                        "Bios:": hw_data.get('bios', 'N/A'),
                        "CPU:": hw_data.get('cpu', 'N/A'),
                        "MAC:": hw_data.get('mac', 'N/A'),
                        "UUID:": hw_data.get('smbios_uuid', 'N/A')
                    }
                    self.update_hardware_tab(hardware_mapping)
                    logger.log_success("Hardware data loaded successfully", "HARDWARE")
                else:
                    logger.log_warning("Hardware data returned empty", "HARDWARE")

                # Load software data
                sw_data = self.controller.hw_reader.get_software_identifiers()
                if sw_data:
                    software_mapping = {
                        "Machine GUID:": sw_data.get('machine_guid', 'N/A'),
                        "FiveM GUID:": sw_data.get('fivem_guid', 'N/A'),
                        "Rockstar GUID:": sw_data.get('rockstar_guid', 'N/A'),
                        "Product ID:": sw_data.get('product_id', 'N/A'),
                        "Installation ID:": sw_data.get('installation_id', 'N/A'),
                        "Windows Activation:": sw_data.get('windows_activation', 'N/A')
                    }
                    self.update_software_tab(software_mapping)
                    logger.log_success("Software data loaded successfully", "SOFTWARE")
                else:
                    logger.log_warning("Software data returned empty", "SOFTWARE")

                return True

            except Exception as e:
                logger.log_error(f"Data loading attempt {attempt + 1} failed: {str(e)}", "SYSTEM")

                if attempt < max_retries - 1:
                    logger.log_info(f"Retrying in {delay}ms...", "SYSTEM")
                    self.root.after(delay, lambda: None)  # Simple delay
                    delay *= 2  # Exponential backoff
                else:
                    logger.log_error("All data loading attempts failed", "SYSTEM")
                    return False

        return False

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

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
        elif "[HARDWARE]" in message or "[SECURITY]" in message:
            tag = "hardware"
        elif "[MAC]" in message:  # ← ADICIONADO: Tag específica para logs MAC
            tag = "mac"
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
            command=self.refresh_all_info,
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
        """Configura a seção esquerda - Spoofing Modules com abas elegantes"""
        # Container principal para Spoofing Modules
        self.spoofing_frame = ctk.CTkFrame(
            self.modules_container,
            fg_color="#1a1a2e",
            corner_radius=15,
            height=320  # Aumentei um pouco para melhor espaçamento
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

        # Container para as abas com borda sutil
        tabs_container = ctk.CTkFrame(
            self.spoofing_frame,
            fg_color="#151525",
            corner_radius=12,
            border_width=1,
            border_color="#2d1152"
        )
        tabs_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Criar abas customizadas
        self.setup_custom_tabs(tabs_container)

    def setup_custom_tabs(self, parent):
        """Configura abas customizadas com visual melhorado"""
        # Container principal das abas
        self.tabs_main_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.tabs_main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame dos cabeçalhos das abas
        self.tab_headers_frame = ctk.CTkFrame(self.tabs_main_frame, fg_color="transparent", height=40)
        self.tab_headers_frame.pack(fill="x", pady=(0, 10))
        self.tab_headers_frame.pack_propagate(False)

        # Conteúdo das abas - frame fixo
        self.tab_content_frame = ctk.CTkFrame(
            self.tabs_main_frame,
            fg_color="transparent"
        )
        self.tab_content_frame.pack(fill="both", expand=True)

        # Criar cabeçalhos das abas
        self.setup_tab_headers()

        # Inicializar frames de conteúdo
        self.tab_frames = {}
        self.current_tab = "HARDWARE"

        # Criar ambos os frames de conteúdo inicialmente
        self.create_tab_content("HARDWARE")
        self.create_tab_content("SOFTWARE")

        # Mostrar aba inicial
        self.show_tab_content("HARDWARE")

    def setup_tab_headers(self):
        """Configura os cabeçalhos das abas com estilo elegante"""
        self.tab_headers = {}

        tabs = [
            ("HARDWARE", "🔩"),
            ("SOFTWARE", "💻")
        ]

        header_container = ctk.CTkFrame(self.tab_headers_frame, fg_color="transparent")
        header_container.pack(fill="both", expand=True)

        for i, (tab_name, icon) in enumerate(tabs):
            # Frame do cabeçalho da aba
            tab_header = ctk.CTkFrame(
                header_container,
                fg_color="#2d1152" if tab_name == "HARDWARE" else "#1a1a2e",
                corner_radius=8,
                border_width=1,
                border_color="#6b21ff" if tab_name == "HARDWARE" else "#2d1152"
            )
            tab_header.pack(side="left", fill="x", expand=True, padx=(5, 5) if i == 0 else 5)

            # Botão da aba (aparentando ser um cabeçalho de aba)
            tab_button = ctk.CTkButton(
                tab_header,
                text=f"{icon} {tab_name}",
                command=lambda tn=tab_name: self.switch_tab(tn),
                fg_color="transparent",
                hover_color="#4a1c6d",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff" if tab_name == "HARDWARE" else "#b0b0ff"
            )
            tab_button.pack(fill="both", expand=True, padx=2, pady=2)

            self.tab_headers[tab_name] = tab_header

    def switch_tab(self, tab_name):
        """Alterna entre as abas"""
        if tab_name == self.current_tab:
            return

        try:
            # Atualizar aparência da aba anterior
            previous_header = self.tab_headers[self.current_tab]
            previous_header.configure(fg_color="#1a1a2e", border_color="#2d1152")

            # Atualizar aparência da nova aba
            new_header = self.tab_headers[tab_name]
            new_header.configure(fg_color="#2d1152", border_color="#6b21ff")

            # Atualizar conteúdo
            self.current_tab = tab_name
            self.show_tab_content(tab_name)

            logger.log_info(f"Switched to {tab_name} tab", "UI")
        except Exception as e:
            logger.log_error(f"Error switching tab: {str(e)}", "ERROR")

    def show_tab_content(self, tab_name):
        """Mostra o conteúdo da aba selecionada"""
        try:
            # Esconder todos os frames primeiro
            for frame_name, frame in self.tab_frames.items():
                if frame and frame.winfo_exists():
                    frame.pack_forget()

            # Mostrar frame da aba atual se existir
            if tab_name in self.tab_frames and self.tab_frames[tab_name] and self.tab_frames[tab_name].winfo_exists():
                self.tab_frames[tab_name].pack(fill="both", expand=True)
            else:
                # Tentar recriar se não existir
                logger.log_warning(f"Tab frame {tab_name} not found, recreating...", "UI")
                self.create_tab_content(tab_name)
                if tab_name in self.tab_frames:
                    self.tab_frames[tab_name].pack(fill="both", expand=True)
                else:
                    logger.log_error(f"Failed to create tab frame for {tab_name}", "ERROR")

        except Exception as e:
            logger.log_error(f"Error showing tab content '{tab_name}': {str(e)}", "ERROR")

    def create_tab_content(self, tab_name):
        """Cria o conteúdo para cada aba e armazena no dicionário"""
        try:
            content_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="transparent")

            if tab_name == "HARDWARE":
                self.setup_hardware_tab(content_frame)
            elif tab_name == "SOFTWARE":
                self.setup_software_tab(content_frame)

            # Armazenar o frame criado no dicionário
            self.tab_frames[tab_name] = content_frame

        except Exception as e:
            logger.log_error(f"Error creating {tab_name} tab content: {str(e)}", "ERROR")
            # Criar um frame de fallback
            fallback_frame = ctk.CTkFrame(self.tab_content_frame, fg_color="transparent")
            error_label = ctk.CTkLabel(
                fallback_frame,
                text=f"Error loading {tab_name} content",
                text_color="#ff4444"
            )
            error_label.pack(expand=True)
            self.tab_frames[tab_name] = fallback_frame

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
            "HWID SPOOFING",
            "MAC SPOOFING",
            "GUID SPOOFING"
        ]

        self.toggle_switches = {}
        for option in toggle_options:
            self.create_toggle_switch(controls_content, option)

    def refresh_hardware_info(self):
        """Atualiza informações de hardware na aba correspondente com loading feedback"""
        try:
            if not self.controller.hw_reader:
                logger.log_error("Hardware reader not available for refresh", "HARDWARE")
                return

            logger.log_info("Refreshing hardware information...", "HARDWARE")

            # Set loading states
            if hasattr(self, 'hardware_labels'):
                for label_text in self.hardware_labels:
                    if label_text in self.hardware_labels and self.hardware_labels[label_text].winfo_exists():
                        self.hardware_labels[label_text].configure(text="Refreshing...", text_color="#ffaa00")

            # Small delay to show loading state
            self.root.after(100, lambda: self._do_refresh_hardware())

        except Exception as e:
            logger.log_error(f"Error initiating hardware refresh: {str(e)}", "HARDWARE")

    def _do_refresh_hardware(self):
        """Internal method to perform hardware refresh"""
        try:
            hw_data = self.controller.hw_reader.get_formatted_hardware_data(self.controller.mac_spoofer)

            if hw_data:
                hardware_mapping = {
                    "Disk C:": hw_data.get('disk_c', 'N/A'),
                    "Disk D:": hw_data.get('disk_d', 'N/A'),
                    "Motherboard:": hw_data.get('motherboard', 'N/A'),
                    "Chassis:": hw_data.get('chassis', 'N/A'),
                    "Bios:": hw_data.get('bios', 'N/A'),
                    "CPU:": hw_data.get('cpu', 'N/A'),
                    "MAC:": hw_data.get('mac', 'N/A'),
                    "UUID:": hw_data.get('smbios_uuid', 'N/A')
                }

                self.update_hardware_tab(hardware_mapping, is_refresh=True)
                logger.log_success("Hardware information refreshed", "HARDWARE")
            else:
                logger.log_warning("Hardware data refresh returned empty", "HARDWARE")
                self._set_hardware_error_states()

        except Exception as e:
            logger.log_error(f"Error refreshing hardware info: {str(e)}", "HARDWARE")
            self._set_hardware_error_states()

    def refresh_software_info(self):
        """Atualiza informações de software na aba correspondente com loading feedback"""
        try:
            if not self.controller.hw_reader:
                logger.log_error("Hardware reader not available for software refresh", "SOFTWARE")
                return

            logger.log_info("Refreshing software information...", "SOFTWARE")

            # Set loading states
            if hasattr(self, 'software_labels'):
                for label_text in self.software_labels:
                    if label_text in self.software_labels and self.software_labels[label_text].winfo_exists():
                        self.software_labels[label_text].configure(text="Refreshing...", text_color="#ffaa00")

            # Small delay to show loading state
            self.root.after(100, lambda: self._do_refresh_software())

        except Exception as e:
            logger.log_error(f"Error initiating software refresh: {str(e)}", "SOFTWARE")

    def _do_refresh_software(self):
        """Internal method to perform software refresh"""
        try:
            sw_data = self.controller.hw_reader.get_software_identifiers()

            if sw_data:
                software_mapping = {
                    "Machine GUID:": sw_data.get('machine_guid', 'N/A'),
                    "FiveM GUID:": sw_data.get('fivem_guid', 'N/A'),
                    "Rockstar GUID:": sw_data.get('rockstar_guid', 'N/A'),
                    "Product ID:": sw_data.get('product_id', 'N/A'),
                    "Installation ID:": sw_data.get('installation_id', 'N/A'),
                    "Windows Activation:": sw_data.get('windows_activation', 'N/A')
                }

                self.update_software_tab(software_mapping, is_refresh=True)
                logger.log_success("Software information refreshed", "SOFTWARE")
            else:
                logger.log_warning("Software data refresh returned empty", "SOFTWARE")
                self._set_software_error_states()

        except Exception as e:
            logger.log_error(f"Error refreshing software info: {str(e)}", "SOFTWARE")
            self._set_software_error_states()

    def refresh_all_info(self):
        """Atualiza as informações de hardware e software na interface com validações robustas"""
        try:
            # Comprehensive validation
            if not hasattr(self, 'controller') or self.controller is None:
                logger.log_error("Controller not initialized", "SYSTEM")
                self.show_toast("Application not properly initialized", "error")
                return

            if not hasattr(self.controller, 'hw_reader') or self.controller.hw_reader is None:
                logger.log_error("Hardware reader not available", "HARDWARE")
                self.show_toast("Hardware reader unavailable", "error")
                return

            # Check if UI components are ready
            if not hasattr(self, 'hardware_labels') or not hasattr(self, 'software_labels'):
                logger.log_error("UI components not ready for refresh", "UI")
                self.show_toast("UI not ready for refresh", "error")
                return

            # Check if labels dictionaries are populated
            if not self.hardware_labels or not self.software_labels:
                logger.log_error("Label dictionaries are empty", "UI")
                self.show_toast("UI labels not initialized", "error")
                return

            logger.log_info("Refreshing hardware and software information...", "SYSTEM")
            self.update_status("Refreshing system information...")

            # Update hardware with error handling
            try:
                self.refresh_hardware_info()
            except Exception as hw_e:
                logger.log_error(f"Hardware refresh failed: {str(hw_e)}", "HARDWARE")
                self._set_hardware_error_states()

            # Update software with error handling
            try:
                self.refresh_software_info()
            except Exception as sw_e:
                logger.log_error(f"Software refresh failed: {str(sw_e)}", "SOFTWARE")
                self._set_software_error_states()

            logger.log_success("Hardware and software info refresh completed", "SYSTEM")
            self.update_status("Information updated", is_success=True)
            self.show_toast("Information updated", "success")

        except Exception as e:
            logger.log_error(f"Critical refresh error: {str(e)}", "SYSTEM")
            self.update_status("Refresh failed", is_error=True)
            self.show_toast("Refresh failed", "error")

    def setup_hardware_tab(self, parent):
        """Configura o conteúdo da aba HARDWARE com layout centralizado"""
        try:
            # Container principal
            main_container = ctk.CTkFrame(parent, fg_color="transparent")
            main_container.pack(fill="both", expand=True)

            # Container scrollable para conteúdo
            scroll_frame = ctk.CTkScrollableFrame(
                main_container,
                fg_color="transparent",
                scrollbar_fg_color="#2d1152",
                scrollbar_button_color="#6b21ff",
                scrollbar_button_hover_color="#4a1c6d"
            )
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Frame para centralizar o conteúdo
            center_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            center_frame.pack(expand=True, fill="both")

            self.hardware_labels = {}
            hardware_data = [
                ("💾", "Disk C:", "disk_c"),
                ("💾", "Disk D:", "disk_d"),
                ("🔩", "Motherboard:", "motherboard"),
                ("📦", "Chassis:", "chassis"),
                ("⚙️", "Bios:", "bios"),
                ("🚀", "CPU:", "cpu"),
                ("🖧", "MAC:", "mac"),
                ("🆔", "UUID:", "smbios_uuid")
            ]

            for icon, label_text, key in hardware_data:
                row_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=6, padx=20)

                # Ícone
                icon_label = ctk.CTkLabel(
                    row_frame,
                    text=icon,
                    text_color="#6b21ff",
                    font=ctk.CTkFont(size=14),
                    width=30
                )
                icon_label.pack(side="left", padx=(0, 10))

                # Label
                text_label = ctk.CTkLabel(
                    row_frame,
                    text=label_text,
                    text_color="#b0b0ff",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=120,
                    anchor="w"
                )
                text_label.pack(side="left", padx=(0, 10))

                # Valor
                value_label = ctk.CTkLabel(
                    row_frame,
                    text="Loading...",
                    text_color="#ffaa00",
                    font=ctk.CTkFont(size=11),
                    anchor="center",
                    wraplength=250
                )
                value_label.pack(side="left", fill="x", expand=True)

                self.hardware_labels[label_text] = value_label

        except Exception as e:
            logger.log_error(f"Error setting up hardware tab: {str(e)}", "ERROR")
        
    def setup_software_tab(self, parent):
        """Configura o conteúdo da aba SOFTWARE com layout centralizado"""
        try:
            # Container principal
            main_container = ctk.CTkFrame(parent, fg_color="transparent")
            main_container.pack(fill="both", expand=True)

            # Container scrollable para conteúdo
            scroll_frame = ctk.CTkScrollableFrame(
                main_container,
                fg_color="transparent",
                scrollbar_fg_color="#2d1152",
                scrollbar_button_color="#6b21ff",
                scrollbar_button_hover_color="#4a1c6d"
            )
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Frame para centralizar o conteúdo
            center_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            center_frame.pack(expand=True, fill="both")

            self.software_labels = {}
            software_data = [
                ("🆔", "Machine GUID:", "machine_guid"),
                ("🎮", "FiveM GUID:", "fivem_guid"),
                ("⭐", "Rockstar GUID:", "rockstar_guid"),
                ("📋", "Product ID:", "product_id"),
                ("🔧", "Installation ID:", "installation_id"),
                ("🪟", "Windows Activation:", "windows_activation")
            ]

            for icon, label_text, key in software_data:
                row_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=6, padx=20)

                # Ícone
                icon_label = ctk.CTkLabel(
                    row_frame,
                    text=icon,
                    text_color="#00ff88",
                    font=ctk.CTkFont(size=14),
                    width=30
                )
                icon_label.pack(side="left", padx=(0, 10))

                # Label
                text_label = ctk.CTkLabel(
                    row_frame,
                    text=label_text,
                    text_color="#b0b0ff",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=120,
                    anchor="w"
                )
                text_label.pack(side="left", padx=(0, 10))

                # Valor
                value_label = ctk.CTkLabel(
                    row_frame,
                    text="Loading...",
                    text_color="#ffaa00",
                    font=ctk.CTkFont(size=11),
                    anchor="center",
                    wraplength=250
                )
                value_label.pack(side="left", fill="x", expand=True)

                self.software_labels[label_text] = value_label

        except Exception as e:
            logger.log_error(f"Error setting up software tab: {str(e)}", "ERROR")

    def _set_hardware_error_states(self):
        """Set error states for hardware labels"""
        try:
            if hasattr(self, 'hardware_labels'):
                for label_text in self.hardware_labels:
                    if label_text in self.hardware_labels and self.hardware_labels[label_text].winfo_exists():
                        self.hardware_labels[label_text].configure(text="Error loading", text_color="#ff4444")
        except Exception as e:
            logger.log_error(f"Error setting hardware error states: {str(e)}", "UI")

    def _set_software_error_states(self):
        """Set error states for software labels"""
        try:
            if hasattr(self, 'software_labels'):
                for label_text in self.software_labels:
                    if label_text in self.software_labels and self.software_labels[label_text].winfo_exists():
                        self.software_labels[label_text].configure(text="Error loading", text_color="#ff4444")
        except Exception as e:
            logger.log_error(f"Error setting software error states: {str(e)}", "UI")

    def update_hardware_tab(self, hardware_mapping, is_refresh=False):
        """Atualiza os labels na aba Hardware com tratamento de erro e color coding"""
        try:
            for key, value in hardware_mapping.items():
                if key in self.hardware_labels and self.hardware_labels[key].winfo_exists():
                    display_value = str(value)
                    if len(display_value) > 30:
                        display_value = display_value[:27] + "..."

                    # Color coding based on value
                    if display_value in ['N/A', 'Error loading', 'Loading...', 'Refreshing...']:
                        text_color = "#ff4444" if display_value == "Error loading" else "#ffaa00" if display_value in ["Loading...", "Refreshing..."] else "#888888"
                    elif "🎭" in display_value:  # Spoofed MAC
                        text_color = "#00ff88"
                    else:  # Normal data
                        text_color = "#ffffff"

                    self.hardware_labels[key].configure(text=display_value, text_color=text_color)

            if is_refresh:
                logger.log_info("Hardware tab updated with refresh data", "UI")

        except Exception as e:
            logger.log_error(f"Error updating hardware tab: {str(e)}", "ERROR")

    def update_software_tab(self, software_mapping, is_refresh=False):
        """Atualiza os labels na aba Software com tratamento de erro e color coding"""
        try:
            for key, value in software_mapping.items():
                if key in self.software_labels and self.software_labels[key].winfo_exists():
                    display_value = str(value)
                    if len(display_value) > 30:
                        display_value = display_value[:27] + "..."

                    # Color coding based on value
                    if display_value in ['N/A', 'Error loading', 'Loading...', 'Refreshing...']:
                        if display_value == "Error loading":
                            text_color = "#ff4444"
                        elif display_value in ["Loading...", "Refreshing..."]:
                            text_color = "#ffaa00"
                        elif display_value == "N/A":
                            text_color = "#888888"
                        else:
                            text_color = "#ffffff"
                    elif "Ativado" in display_value or "Activated" in display_value:
                        text_color = "#00ff88"  # Green for activated Windows
                    elif "Não Instalado" in display_value or "Not Installed" in display_value:
                        text_color = "#ffaa00"  # Orange for not installed
                    elif "Erro" in display_value or "Error" in display_value:
                        text_color = "#ff4444"  # Red for errors
                    else:
                        text_color = "#ffffff"  # White for normal data

                    self.software_labels[key].configure(text=display_value, text_color=text_color)

            if is_refresh:
                logger.log_info("Software tab updated with refresh data", "UI")

        except Exception as e:
            logger.log_error(f"Error updating software tab: {str(e)}", "ERROR")



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
            
            # Handle specific toggles
            if option == "MAC SPOOFING":
                self.on_mac_toggle_changed()
            # Adicione outros handlers aqui para HWID, EFI, etc.
                
        else:
            self.show_toast(f"{option} deactivated", "info")
            
            # Handle toggle deactivation
            if option == "MAC SPOOFING":
                self.on_mac_reset()

    def on_mac_toggle_changed(self):
        """Handle MAC spoofing activation"""
        logger.log_info("MAC spoofing requested", "MAC")
        
        # Show interface selection dialog
        dialog = InterfaceSelectionDialog(self.root, self.controller.mac_spoofer)
        selected_interface, vendor_oui, selected_mac = dialog.show()
        # If user selected an interface, store it and notify user. Do NOT perform spoof now.
        if selected_interface:
            self.selected_interface = selected_interface
            self.selected_vendor = vendor_oui
            self.selected_mac = selected_mac
            logger.log_info(f"MAC selection stored for {selected_interface} (vendor={vendor_oui})", "MAC")
            self.show_toast("MAC interface selected. Spoof will run when you Start Spoofing.", "info")
        else:
            # User cancelled, reset the toggle and clear selection
            self.toggle_switches["MAC SPOOFING"].deselect()
            self.toggle_states["MAC SPOOFING"] = False
            self.selected_interface = None
            self.selected_vendor = None
            self.selected_mac = None
            logger.log_info("MAC spoofing cancelled by user", "MAC")

    def execute_mac_spoofing(self, interface_name, vendor_oui):
        """Execute MAC spoofing in background thread"""
        try:
            logger.log_info(f"Starting MAC spoofing on {interface_name}", "MAC")
            self.update_status(f"Spoofing MAC on {interface_name}...")
            
            success = self.controller.mac_spoofer.spoof_mac_address(interface_name, vendor_oui)
            
            if success:
                logger.log_success(f"MAC spoofing completed on {interface_name}", "MAC")
                self.show_toast("MAC address spoofed successfully!", "success")
                
                # Refresh hardware info to show new MAC
                self.root.after(1000, self.refresh_hardware_info)
            else:
                logger.log_error(f"MAC spoofing failed on {interface_name}", "MAC")
                self.show_toast("MAC spoofing failed!", "error")
                
                # Reset the toggle on failure
                self.root.after(0, self.reset_mac_toggle)
                
        except Exception as e:
            logger.log_error(f"MAC spoofing error: {str(e)}", "MAC")
            self.show_toast("MAC spoofing error occurred!", "error")
            self.root.after(0, self.reset_mac_toggle)

    def on_mac_reset(self):
        """Handle MAC reset (when toggle is turned off)"""
        logger.log_info("MAC reset requested", "MAC")
        
        if self.controller.mac_spoofer.current_interface:
            thread = threading.Thread(
                target=self.execute_mac_reset,
                args=(self.controller.mac_spoofer.current_interface,),
                daemon=True
            )
            thread.start()
        else:
            logger.log_warning("No active MAC spoofing session to reset", "MAC")
            self.show_toast("No active MAC spoofing to reset", "info")

    def execute_mac_reset(self, interface_name):
        """Execute MAC reset in background thread"""
        try:
            logger.log_info(f"Resetting MAC on {interface_name}", "MAC")
            self.update_status(f"Resetting MAC on {interface_name}...")
            
            success = self.controller.mac_spoofer.reset_mac_address(interface_name)
            
            if success:
                logger.log_success(f"MAC reset completed on {interface_name}", "MAC")
                self.show_toast("MAC address reset to original!", "success")
                
                # Refresh hardware info to show original MAC
                self.root.after(1000, self.refresh_hardware_info)
            else:
                logger.log_error(f"MAC reset failed on {interface_name}", "MAC")
                self.show_toast("MAC reset failed!", "error")
                
        except Exception as e:
            logger.log_error(f"MAC reset error: {str(e)}", "MAC")
            self.show_toast("MAC reset error occurred!", "error")

    def reset_mac_toggle(self):
        """Reset MAC toggle to off state"""
        self.toggle_switches["MAC SPOOFING"].deselect()
        self.toggle_states["MAC SPOOFING"] = False

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
        self.logs_text.tag_config("hardware", foreground="#b0b0ff")
        self.logs_text.tag_config("mac", foreground="#b0b0ff")  # ← ADICIONADO: Cor para logs MAC
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
            "🚨 CONFIRM SPOOFING",
            "⚠️  WARNING: This will PERFORM SYSTEM MODIFICATIONS:\n\n"
            "• TERMINATE Discord, FiveM, Steam processes\n" 
            "• RENAME Discord RPC folders to break tracking\n"
            "• CLEAN FiveM cache and registry traces\n"
            "• RESET network configurations\n"
            "• DELETE temporary system files\n\n"
            "✅ This is NOT a simulation - changes will be made!\n\n"
            "Continue with spoofing protocol?",
            icon='warning'
        )
        
        if not confirm:
            logger.log_warning("Spoofing cancelled by user", "USER")
            return

        self.start_spoofing()

    def start_spoofing(self):
        self.cleaning_in_progress = True
        self.spoof_button.configure(state="disabled", text="🔄 SPOOFING...")
        self.spoof_button.start_pulse()
        self.clear_logs()
        self.update_status("Executing spoofing protocol")
        self.circular_progress.set_progress(0)
        
        enabled_modules = [module for module, state in self.toggle_states.items() if state]
        if enabled_modules:
            logger.log_info(f"Active: {', '.join(enabled_modules)}", "MODULES")
        
        self.show_toast("Starting spoofing...", "info")
        
        self.controller.start_spoofing_thread(
            self.toggle_states,
            self.selected_interface,
            self.selected_vendor,
            self.selected_mac
        )

    def handle_spoofing_start(self):
        """Callback: Ações de UI quando o spoofing começa."""
        # Este método já é chamado em start_spoofing, então podemos manter simples
        pass

    def handle_spoofing_success(self):
        """Callback: Ações de UI em caso de sucesso."""
        self.last_spoof_time = self.controller.last_spoof_time
        if self.controller.hw_reader:
            logger.log_info("Refreshing hardware and software display after spoof...", "SYSTEM")
            self.refresh_all_info()
        
        self.circular_progress.set_progress(100)
        self.update_status("Spoofing completed!", is_success=True)
        self.show_toast("System successfully spoofed!", "success")

    def handle_spoofing_failure(self, reason=""):
        """Callback: Ações de UI em caso de falha."""
        self.circular_progress.set_progress(75) # Progresso parcial
        self.update_status(reason, is_error=True)
        self.show_toast(f"Spoofing failed: {reason}", "error")

    def handle_spoofing_finish(self):
        """Callback: Ações de UI ao finalizar (sucesso ou falha)."""
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
        """TODO: Integrar painel de dashboard com estatísticas detalhadas"""
        self.show_toast("Dashboard loaded", "info")
        logger.log_info("Dashboard panel opened - TODO: Implement detailed statistics", "NAVIGATION")

    def show_spoof_tools(self):
        """TODO: Integrar ferramentas avançadas de spoofing"""
        self.show_toast("Spoof tools panel", "info")
        logger.log_info("Spoof tools panel opened - TODO: Implement advanced spoofing tools", "NAVIGATION")

    def show_history(self):
        """TODO: Integrar histórico de operações"""
        self.show_toast("History panel", "info")
        logger.log_info("History panel opened - TODO: Implement operation history", "NAVIGATION")

    def show_settings(self):
        """TODO: Integrar configurações avançadas"""
        self.show_toast("Settings panel", "info")
        logger.log_info("Settings panel opened - TODO: Implement advanced settings", "NAVIGATION")

    def show_about(self):
        from tkinter import messagebox
        about_text = """
        Midnight Spoofer Beta
        Advanced system identity protection
        
        • Discord RPC spoofing
        • FiveM cache cleaning
        • Network configuration reset
        • Registry sanitization
        • Hardware ID detection
        • MAC Address spoofing 🆕
        
        ⚠️ Always run as Administrator
        for full functionality.
        
        📌 Educational purposes only
        
        🚧 Under active development
        """   
        messagebox.showinfo("About Midnight Spoofer", about_text)

    def run(self):
        self.root.mainloop()
