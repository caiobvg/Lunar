import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
from PIL import Image, ImageDraw
import os
import sys
import threading
import time
import queue

# Relative module imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from cleaners.system_cleaner import SystemCleaner
from utils.logger import logger

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, event):
        self.configure(fg_color="#4a1c6d")
        
    def on_leave(self, event):
        self.configure(fg_color="#2d1152")

class MidnightSpooferGUI:
    def __init__(self):
        # Configure custom theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Midnight Spoofer v1.0")
        self.root.geometry("1000x800")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#0a0a1a")
        
        # Center window
        self.center_window()
        
        # Queue for thread-safe communication
        self.log_queue = queue.Queue()
        
        # Initialize cleaner with real-time callback
        self.cleaner = SystemCleaner(realtime_callback=self.add_log_realtime)
        
        # Control variables
        self.cleaning_in_progress = False
        self.animation_running = False
        
        # Setup interface
        self.setup_ui()
        
        # Start real-time log processing
        self.process_log_queue()
        
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
            # Schedule next check
            self.root.after(100, self.process_log_queue)
    
    def add_log_ui(self, message):
        """Add log to interface (must be called only in main thread)"""
        self.logs_text.insert("end", f"{message}\n")
        self.logs_text.see("end")
        self.root.update_idletasks()
        
    def setup_ui(self):
        """Setup premium user interface"""
        # Main frame with gradient
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color="#0a0a1a",
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True)
        
        # Header with gradient
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent",
            height=180
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Main title
        title_label = ctk.CTkLabel(
            header_frame,
            text="MIDNIGHT SPOOFER",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(40, 0))
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Advanced System Identity Protection",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color="#b0b0ff"
        )
        subtitle_label.pack(pady=(5, 20))
        
        # Center container
        center_container = ctk.CTkFrame(
            main_frame,
            fg_color="transparent"
        )
        center_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Main spoof button
        self.spoof_button = AnimatedButton(
            center_container,
            text="SPOOF",
            command=self.start_spoofing,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            height=80,
            width=400,
            fg_color="#2d1152",
            hover_color="#4a1c6d",
            text_color="#ffffff",
            corner_radius=20,
            border_width=3,
            border_color="#6b21ff"
        )
        self.spoof_button.pack(pady=(0, 30))
        
        # Spoof status
        self.status_frame = ctk.CTkFrame(
            center_container,
            fg_color="#1a1a2e",
            corner_radius=15,
            height=60
        )
        self.status_frame.pack(fill="x", pady=(0, 20))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="SYSTEM READY - AWAITING COMMAND",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#00ff88"
        )
        self.status_label.pack(expand=True)
        
        # Logs area
        logs_container = ctk.CTkFrame(
            center_container,
            fg_color="#1a1a2e",
            corner_radius=15
        )
        logs_container.pack(fill="both", expand=True)
        
        logs_header = ctk.CTkFrame(
            logs_container,
            fg_color="transparent",
            height=40
        )
        logs_header.pack(fill="x", padx=20, pady=(10, 0))
        logs_header.pack_propagate(False)
        
        logs_title = ctk.CTkLabel(
            logs_header,
            text="EXECUTION LOG - REAL TIME",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#ffffff"
        )
        logs_title.pack(side="left")
        
        clear_btn = ctk.CTkButton(
            logs_header,
            text="CLEAR LOGS",
            command=self.clear_logs,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=80,
            height=25,
            fg_color="#2d1152",
            hover_color="#4a1c6d"
        )
        clear_btn.pack(side="right")
        
        self.logs_text = ctk.CTkTextbox(
            logs_container,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            fg_color="#0f0f23",
            text_color="#e0e0ff",
            border_width=2,
            border_color="#2d1152",
            corner_radius=10
        )
        self.logs_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            center_container,
            height=8,
            fg_color="#1a1a2e",
            progress_color="#6b21ff",
            corner_radius=4
        )
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.set(0)
        
        # Footer
        footer_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent",
            height=50
        )
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        footer_label = ctk.CTkLabel(
            footer_frame,
            text="Midnight Spoofer v1.0 | Advanced System Protection",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#8888ff"
        )
        footer_label.pack(expand=True)
        
        # Add initial logs
        self.add_log_ui("[SYSTEM] Midnight Spoofer initialized successfully")
        self.add_log_ui("[STATUS] Security protocols loaded and ready")
        self.add_log_ui("[COMMAND] Click SPOOF to initiate protocol")
        
    def update_status(self, message, is_error=False, is_success=False):
        """Update status in interface"""
        if is_error:
            color = "#ff4444"
            prefix = "ERROR: "
        elif is_success:
            color = "#00ff88"
            prefix = "COMPLETE: "
        else:
            color = "#ffaa00"
            prefix = "EXECUTING: "
            
        self.status_label.configure(text=f"{prefix}{message}", text_color=color)
        
    def add_log(self, message):
        """Maintained for compatibility"""
        self.add_log_ui(message)
        
    def clear_logs(self):
        """Clear logs"""
        self.logs_text.delete("1.0", "end")
        self.add_log_ui("[SYSTEM] Log cleared")
        
    def animate_button(self):
        """Button animation during spoofing"""
        colors = ["#2d1152", "#3a1668", "#471c7e", "#542194", "#6127aa"]
        current = 0
        
        def update_color():
            nonlocal current
            if self.animation_running:
                self.spoof_button.configure(fg_color=colors[current])
                current = (current + 1) % len(colors)
                self.root.after(200, update_color)
        
        self.animation_running = True
        update_color()
        
    def stop_animation(self):
        """Stop button animation"""
        self.animation_running = False
        self.spoof_button.configure(fg_color="#2d1152")
        
    def start_spoofing(self):
        """Start complete spoofing in separate thread"""
        if self.cleaning_in_progress:
            return
            
        self.cleaning_in_progress = True
        self.spoof_button.configure(state="disabled", text="SPOOFING...")
        self.clear_logs()
        self.update_status("Spoofing protocol active")
        self.progress_bar.set(0)
        
        # Start animation
        self.animate_button()
        
        thread = threading.Thread(target=self.execute_spoofing)
        thread.daemon = True
        thread.start()
        
    def execute_spoofing(self):
        """Execute complete spoofing"""
        try:
            # Execute complete spoofing
            logs = self.cleaner.execute_full_spoof()
            
            self.progress_bar.set(1)
            self.update_status("Spoofing protocol completed", is_success=True)
            
        except Exception as e:
            self.add_log_realtime(f"[ERROR] CRITICAL FAILURE IN SPOOFING PROTOCOL: {str(e)}")
            self.update_status("Protocol failure", is_error=True)
        finally:
            self.cleaning_in_progress = False
            self.spoof_button.configure(state="normal", text="SPOOF")
            self.stop_animation()
            
    def run(self):
        """Start application"""
        self.root.mainloop()

def main():
    app = MidnightSpooferGUI()
    app.run()

if __name__ == "__main__":
    main()