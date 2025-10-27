import customtkinter as ctk
import threading
import time
import queue
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the cleaner
from cleaners.system_cleaner import SystemCleaner

# Import GUI components
from .components.particles import ParticleSystem
from .components.buttons import AnimatedButton
from .components.progress import CircularProgress
from .components.toast import ToastNotification
from .components.stats import SystemStats

class MidnightSpooferGUI:
    def __init__(self):
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Midnight Spoofer v2.0 - REAL SPOOFING")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.configure(fg_color="#0a0a1a")
        
        # Center window
        self.center_window()
        
        # Queue for thread-safe communication
        self.log_queue = queue.Queue()
        
        # Use the SystemCleaner
        self.cleaner = SystemCleaner(realtime_callback=self.add_log_realtime)
        
        # Control variables
        self.cleaning_in_progress = False
        self.sidebar_expanded = True
        self.current_theme = "purple"
        
        # Statistics
        self.total_spoofs = 0
        self.last_spoof_time = None
        
        # Setup interface
        self.setup_ui()
        
        # Start real-time log processing
        self.process_log_queue()
        self.update_system_stats()
        
        # Add initial logs
        self.add_log_ui("[SYSTEM] Midnight Spoofer Premium INITIALIZED")
        self.add_log_ui("[SECURITY] REAL spoofing engine loaded")
        self.add_log_ui("[READY] Discord/FiveM spoofing ready")
        self.add_log_ui("[INFO] Run as Administrator for full functionality")

    def center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def add_log_realtime(self, message):
        """Add log to queue (thread-safe)"""
        if self.log_queue:
            self.log_queue.put(message)

    def process_log_queue(self):
        """Process log queue in main thread"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.add_log_ui(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

    def add_log_ui(self, message):
        """Add log to interface with syntax highlighting"""
        # Simple syntax highlighting
        if message.startswith("[ERROR]") or "ERROR" in message:
            tag = "error"
        elif message.startswith("[SUCCESS]") or "SUCCESS" in message or "✅" in message:
            tag = "success"
        elif message.startswith("[WARNING]") or "WARNING" in message or "⚠️" in message:
            tag = "warning"
        elif message.startswith("[SYSTEM]") or message.startswith("[STATUS]") or message.startswith("[INFO]"):
            tag = "system"
        elif message.startswith("[REAL]"):
            tag = "real"
        else:
            tag = "info"
        
        self.logs_text.configure(state="normal")
        self.logs_text.insert("end", f"{message}\n", tag)
        self.logs_text.see("end")
        self.logs_text.configure(state="disabled")

    def setup_ui(self):
        """Setup premium user interface with all effects"""
        # Main layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.setup_sidebar()
        
        # Main content area
        self.main_content = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(1, weight=1)
        
        # Header
        self.setup_header()
        
        # Dashboard
        self.setup_dashboard()
        
        # Setup log syntax highlighting
        self.setup_log_highlighting()

    def setup_sidebar(self):
        """Setup animated sidebar"""
        # Use solid colors instead of alpha
        self.sidebar = ctk.CTkFrame(self.root, fg_color="#1a1a2e", width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Sidebar content
        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo
        logo_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(0, 30))
        
        logo_label = ctk.CTkLabel(logo_frame, text="🌙 MIDNIGHT", 
                                 font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                                 text_color="#6b21ff")
        logo_label.pack(side="left")
        
        # Navigation buttons
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
        
        # Theme switcher
        theme_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        theme_frame.pack(side="bottom", fill="x", pady=20)
        
        ctk.CTkLabel(theme_frame, text="THEME", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        
        theme_options = ctk.CTkSegmentedButton(theme_frame, values=["Purple", "Cyan", "Red"],
                                              command=self.switch_theme)
        theme_options.pack(fill="x", pady=5)
        theme_options.set("Purple")

    def setup_header(self):
        """Setup header with stats cards"""
        header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent", height=120)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stats cards - use solid colors
        self.cpu_card = self.create_stat_card(header_frame, "CPU", "0%", 0, "#6b21ff")
        self.cpu_card.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.memory_card = self.create_stat_card(header_frame, "Memory", "0%", 1, "#00ff88")
        self.memory_card.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.disk_card = self.create_stat_card(header_frame, "Disk", "0%", 2, "#ffaa00")
        self.disk_card.grid(row=0, column=2, padx=5, sticky="ew")
        
        self.spoofs_card = self.create_stat_card(header_frame, "Total Spoofs", "0", 3, "#ff4444")
        self.spoofs_card.grid(row=0, column=3, padx=(10, 0), sticky="ew")

    def create_stat_card(self, parent, title, value, column, color):
        """Create a stat card with progress bar"""
        # Use solid color instead of GlassFrame
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=15)
        
        # Content
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

    def setup_dashboard(self):
        """Setup main dashboard"""
        # Content area
        content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Main action area
        action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Circular progress with main button
        progress_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        progress_frame.pack(side="left", padx=(0, 20))
        
        self.circular_progress = CircularProgress(progress_frame, size=200)
        self.circular_progress.pack(pady=20)
        
        # Main spoof button
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
        
        # Status display - use solid color
        self.status_frame = ctk.CTkFrame(action_frame, fg_color="#1a1a2e", corner_radius=15, height=80)
        self.status_frame.pack(side="right", fill="both", expand=True)
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="🟢 SYSTEM READY - AWAITING COMMAND",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#00ff88"
        )
        self.status_label.pack(expand=True)
        
        # Logs area
        self.setup_logs_area(content_frame)

    def setup_logs_area(self, parent):
        """Setup advanced logs area"""
        # Use solid color instead of GlassFrame
        logs_container = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=15)
        logs_container.grid(row=1, column=0, sticky="nsew")
        logs_container.grid_columnconfigure(0, weight=1)
        logs_container.grid_rowconfigure(1, weight=1)
        
        # Logs header with controls
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
        
        # Log controls
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
        
        # Logs text area
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
        """Setup syntax highlighting for logs"""
        self.logs_text.tag_config("error", foreground="#ff4444")
        self.logs_text.tag_config("success", foreground="#00ff88")
        self.logs_text.tag_config("warning", foreground="#ffaa00")
        self.logs_text.tag_config("system", foreground="#6b21ff")
        self.logs_text.tag_config("real", foreground="#b0b0ff")
        self.logs_text.tag_config("info", foreground="#e0e0ff")

    def update_system_stats(self):
        """Update system statistics in real-time"""
        try:
            cpu_usage = SystemStats.get_cpu_usage()
            memory_usage = SystemStats.get_memory_usage()
            disk_usage = SystemStats.get_disk_usage()
            
            # Update cards
            self.update_stat_card(self.cpu_card, f"{cpu_usage:.1f}%", cpu_usage/100)
            self.update_stat_card(self.memory_card, f"{memory_usage:.1f}%", memory_usage/100)
            self.update_stat_card(self.disk_card, f"{disk_usage:.1f}%", disk_usage/100)
            self.update_stat_card(self.spoofs_card, str(self.total_spoofs), min(self.total_spoofs/10, 1))
            
        except Exception as e:
            print(f"Error updating stats: {e}")
        
        self.root.after(2000, self.update_system_stats)

    def update_stat_card(self, card, value, progress):
        """Update individual stat card"""
        for widget in card.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                if widget.cget("text").isdigit() or "%" in widget.cget("text"):
                    widget.configure(text=value)
            elif isinstance(widget, ctk.CTkProgressBar):
                widget.set(progress)

    def show_toast(self, message, toast_type="info"):
        """Show toast notification"""
        ToastNotification(self.root, message, toast_type)

    def switch_theme(self, theme):
        """Switch between color themes"""
        self.current_theme = theme.lower()
        # This would update all colors in the interface
        self.show_toast(f"Theme switched to {theme}", "info")

    def start_spoofing_sequence(self):
        """Start the spoofing sequence with confirmation"""
        if self.cleaning_in_progress:
            return
        
        # Import messagebox here to avoid circular imports
        from tkinter import messagebox
            
        # Confirmation dialog
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
            self.add_log_ui("[USER] Spoofing cancelled by user")
            return
            
        self.start_spoofing()

    def start_spoofing(self):
        """Start REAL spoofing"""
        self.cleaning_in_progress = True
        self.spoof_button.configure(state="disabled", text="🔄 REAL SPOOFING...")
        self.spoof_button.start_pulse()
        self.clear_logs()
        self.update_status("Executing REAL spoofing protocol")
        self.circular_progress.set_progress(0)
        
        self.show_toast("Starting REAL spoofing...", "info")
        
        # Start in separate thread
        thread = threading.Thread(target=self.execute_spoofing)
        thread.daemon = True
        thread.start()

    def execute_spoofing(self):
        """Execute REAL spoofing using SystemCleaner"""
        try:
            self.add_log_ui("=" * 60)
            self.add_log_ui("[REAL] 🚀 INITIATING REAL SPOOFING PROTOCOL")
            self.add_log_ui("[REAL] This will actually modify system files")
            self.add_log_ui("=" * 60)
            
            # ✅ EXECUTE REAL SPOOFING using the cleaner!
            success = self.cleaner.execute_real_spoofing()
            
            if success:
                self.total_spoofs += 1
                self.last_spoof_time = datetime.now()
                
                self.circular_progress.set_progress(100)
                self.update_status("REAL spoofing completed!", is_success=True)
                self.show_toast("Discord successfully spoofed!", "success")
                self.add_log_ui("[SUCCESS] ✅ REAL SPOOFING COMPLETED!")
                self.add_log_ui("[SECURITY] Discord RPC has been modified")
                self.add_log_ui("[SECURITY] FiveM cache has been cleared")
                self.add_log_ui(f"[STATS] Total real spoofs: {self.total_spoofs}")
            else:
                self.circular_progress.set_progress(75)
                self.update_status("Some operations failed", is_error=True)
                self.show_toast("Some spoofing operations failed", "warning")
                self.add_log_ui("[WARNING] ⚠️  Some spoofing operations may have failed")
            
        except Exception as e:
            self.add_log_ui(f"[CRITICAL] Spoofing failed completely: {str(e)}")
            self.update_status("Critical failure", is_error=True)
            self.show_toast("Spoofing failed critically!", "error")
        finally:
            self.cleaning_in_progress = False
            self.spoof_button.configure(state="normal", text="🚀 START SPOOFING")
            self.spoof_button.stop_pulse()

    def update_status(self, message, is_error=False, is_success=False):
        """Update status in interface"""
        if is_error:
            color = "#ff4444"
            icon = "🔴"
        elif is_success:
            color = "#00ff88"
            icon = "🟢"
        else:
            color = "#ffaa00"
            icon = "🟡"
            
        self.status_label.configure(text=f"{icon} {message}", text_color=color)

    def clear_logs(self):
        """Clear logs"""
        self.logs_text.configure(state="normal")
        self.logs_text.delete("1.0", "end")
        self.logs_text.configure(state="disabled")
        self.add_log_ui("[SYSTEM] Log cleared")
        self.show_toast("Logs cleared", "info")

    def export_logs(self):
        """Export logs to file"""
        try:
            filename = f"midnight_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.logs_text.get("1.0", "end"))
            self.show_toast(f"Logs exported to {filename}", "success")
        except Exception as e:
            self.show_toast(f"Export failed: {str(e)}", "error")

    # Navigation methods
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
        about_text = """Midnight Spoofer v2.0 - REAL

Advanced system identity protection
• Real Discord RPC spoofing
• FiveM cache cleaning
• Network configuration reset
• Registry sanitization

⚠️ Always run as Administrator
for full functionality."""
        
        messagebox.showinfo("About Midnight Spoofer", about_text)

    def run(self):
        """Start application"""
        self.root.mainloop()