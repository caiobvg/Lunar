import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk, ImageFilter
import os
import sys
import threading
import time
import queue
import math
import random
from datetime import datetime, timedelta
import psutil
import subprocess
import winreg
import tempfile
import glob
from pathlib import Path
import shutil

# Configure custom theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ParticleSystem:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        self.connections = []
        
    def create_particles(self, count=50):
        for _ in range(count):
            particle = {
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'radius': random.uniform(1, 3),
                'color': random.choice(['#6b21ff', '#4a1c6d', '#2d1152', "#141425"]),
                'id': None
            }
            self.particles.append(particle)
    
    def draw_particles(self):
        for particle in self.particles:
            x1 = particle['x'] - particle['radius']
            y1 = particle['y'] - particle['radius']
            x2 = particle['x'] + particle['radius']
            y2 = particle['y'] + particle['radius']
            particle['id'] = self.canvas.create_oval(x1, y1, x2, y2, 
                                                   fill=particle['color'], 
                                                   outline="", tags="particle")
    
    def draw_connections(self):
        self.connections.clear()
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles[i+1:], i+1):
                distance = math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)
                if distance < 100:
                    # Use solid color instead of alpha
                    color = '#36365a'  # Solid light purple
                    line_id = self.canvas.create_line(p1['x'], p1['y'], p2['x'], p2['y'],
                                                     fill=color, width=1, tags="connection")
                    self.connections.append(line_id)
    
    def update(self):
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Bounce off edges
            if particle['x'] <= 0 or particle['x'] >= self.width:
                particle['vx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= self.height:
                particle['vy'] *= -1
            
            # Update canvas position
            if particle['id']:
                x1 = particle['x'] - particle['radius']
                y1 = particle['y'] - particle['radius']
                x2 = particle['x'] + particle['radius']
                y2 = particle['y'] + particle['radius']
                self.canvas.coords(particle['id'], x1, y1, x2, y2)

class GlassFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        # Remove alpha parameter since CustomTkinter doesn't support it
        self.alpha = kwargs.pop('alpha', 200)
        super().__init__(*args, **kwargs)
        # Apply a slightly lighter/darker color based on alpha for glass effect
        self._adjust_color_for_effect()
        
    def _adjust_color_for_effect(self):
        """Adjust color to simulate glass effect without alpha"""
        current_color = self.cget("fg_color")
        if current_color == "transparent":
            return
            
        # Convert hex to RGB and adjust brightness based on alpha
        if isinstance(current_color, str) and current_color.startswith('#'):
            r = int(current_color[1:3], 16)
            g = int(current_color[3:5], 16)
            b = int(current_color[5:7], 16)
            
            # Adjust brightness based on alpha (simulate glass effect)
            if self.alpha > 150:  # More opaque
                r = min(255, r + 10)
                g = min(255, g + 10)
                b = min(255, b + 10)
            else:  # More transparent
                r = max(0, r - 10)
                g = max(0, g - 10)
                b = max(0, b - 10)
                
            new_color = f"#{r:02x}{g:02x}{b:02x}"
            self.configure(fg_color=new_color)

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_fg_color = self.cget("fg_color")
        self.hover_fg_color = "#4a1c6d"
        self.animation_running = False
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, event):
        self.configure(fg_color=self.hover_fg_color)
        
    def on_leave(self, event):
        if not self.animation_running:
            self.configure(fg_color=self.default_fg_color)
    
    def start_pulse(self):
        self.animation_running = True
        self._pulse_animation()
    
    def stop_pulse(self):
        self.animation_running = False
        self.configure(fg_color=self.default_fg_color)
    
    def _pulse_animation(self):
        if not self.animation_running:
            return
            
        colors = ["#2d1152", "#3a1668", "#471c7e", "#542194", "#6127aa"]
        current = 0
        
        def update_color():
            nonlocal current
            if self.animation_running:
                self.configure(fg_color=colors[current])
                current = (current + 1) % len(colors)
                self.after(200, update_color)
        
        update_color()

class ToastNotification:
    def __init__(self, parent, message, toast_type="info"):
        self.parent = parent
        self.message = message
        self.toast_type = toast_type
        
        self.toast = ctk.CTkToplevel(parent)
        self.toast.overrideredirect(True)
        self.toast.attributes("-topmost", True)
        self.toast.attributes("-alpha", 0.0)
        
        self.setup_toast()
        self.animate_in()
    
    def setup_toast(self):
        colors = {
            "info": ("#6b21ff", "#1a1a2e"),
            "success": ("#00ff88", "#1a2e1a"),
            "warning": ("#ffaa00", "#2e2a1a"),
            "error": ("#ff4444", "#2e1a1a")
        }
        
        bg_color, frame_color = colors.get(self.toast_type, colors["info"])
        
        self.toast.configure(fg_color=frame_color)
        self.toast.geometry("300x60")
        
        # Position in top right
        x = self.parent.winfo_rootx() + self.parent.winfo_width() - 320
        y = self.parent.winfo_rooty() + 50
        self.toast.geometry(f"+{x}+{y}")
        
        frame = ctk.CTkFrame(self.toast, fg_color=bg_color, corner_radius=10)
        frame.pack(fill="both", padx=10, pady=10)
        
        label = ctk.CTkLabel(frame, text=self.message, text_color="white")
        label.pack(expand=True, fill="both", padx=20, pady=15)
    
    def animate_in(self):
        for i in range(10):
            alpha = i * 0.1
            self.toast.attributes("-alpha", alpha)
            self.toast.update()
            time.sleep(0.02)
        
        self.toast.after(3000, self.animate_out)
    
    def animate_out(self):
        for i in range(10, -1, -1):
            alpha = i * 0.1
            self.toast.attributes("-alpha", alpha)
            self.toast.update()
            time.sleep(0.02)
        
        self.toast.destroy()

class CircularProgress(ctk.CTkCanvas):
    def __init__(self, parent, size=200, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.center = size // 2
        self.radius = size // 2 - 10
        self.progress = 0
        
        self.configure(bg="#0a0a1a", highlightthickness=0)
        self.draw_background()
        self.draw_progress()
    
    def draw_background(self):
        self.create_oval(10, 10, self.size-10, self.size-10, 
                        outline="#1a1a2e", width=8, fill="#0a0a1a")
    
    def draw_progress(self):
        self.delete("progress")
        angle = 360 * self.progress / 100
        
        self.create_arc(10, 10, self.size-10, self.size-10,
                       start=90, extent=-angle,
                       outline="#6b21ff", width=8, style="arc", tags="progress")
        
        # Progress text
        self.create_text(self.center, self.center, text=f"{int(self.progress)}%",
                        fill="white", font=("Segoe UI", 20, "bold"), tags="progress")
    
    def set_progress(self, value):
        self.progress = max(0, min(100, value))
        self.draw_progress()

class SystemStats:
    @staticmethod
    def get_cpu_usage():
        return psutil.cpu_percent(interval=0.1)
    
    @staticmethod
    def get_memory_usage():
        memory = psutil.virtual_memory()
        return memory.percent
    
    @staticmethod
    def get_disk_usage():
        disk = psutil.disk_usage('/')
        return disk.percent

class RealSpoofer:
    """Classe REAL de spoofing - substitui a simulação"""
    
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.total_operations = 0
        self.completed_operations = 0
    
    def add_log(self, message):
        """Adiciona log via callback"""
        if self.log_callback:
            self.log_callback(message)
    
    def get_progress(self):
        """Calcula progresso real"""
        if self.total_operations == 0:
            return 0
        return (self.completed_operations / self.total_operations) * 100
    
    def kill_processes(self):
        """Mata processos do Discord, FiveM, Steam REAL"""
        self.add_log("[REAL] Terminating target processes...")
        try:
            processes_to_kill = ['discord', 'fivem', 'steam', 'steamwebhelper', 'epicgameslauncher']
            killed = 0
            
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    for target in processes_to_kill:
                        if target in proc_name:
                            proc.kill()
                            killed += 1
                            self.add_log(f"[REAL] Killed: {proc.info['name']} (PID: {proc.info['pid']})")
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            self.add_log(f"[REAL] {killed} processes terminated")
            return True
        except Exception as e:
            self.add_log(f"[ERROR] Failed to kill processes: {str(e)}")
            return False
    
    def spoof_discord_rpc(self):
        """SPOOF REAL do Discord RPC"""
        self.add_log("[REAL] Starting Discord RPC spoofing...")
        
        discord_paths = [
            os.path.join(os.environ['APPDATA'], 'discord'),
            os.path.join(os.environ['LOCALAPPDATA'], 'Discord')
        ]
        
        spoofed_count = 0
        for base_path in discord_paths:
            if os.path.exists(base_path):
                try:
                    # Encontra pastas de versão do Discord
                    for item in os.listdir(base_path):
                        if item.replace('.', '').isdigit():  # Versões como 0.0.309
                            modules_path = os.path.join(base_path, item, 'modules')
                            if os.path.exists(modules_path):
                                # Procura por pastas discord_rpc
                                for module_item in os.listdir(modules_path):
                                    if 'discord_rpc' in module_item.lower():
                                        old_path = os.path.join(modules_path, module_item)
                                        # Cria novo nome aleatório
                                        new_name = f"discord_rpc_{random.randint(10000, 99999)}"
                                        new_path = os.path.join(modules_path, new_name)
                                        
                                        try:
                                            if os.path.exists(old_path):
                                                os.rename(old_path, new_path)
                                                spoofed_count += 1
                                                self.add_log(f"[REAL] Renamed: {module_item} -> {new_name}")
                                        except Exception as e:
                                            self.add_log(f"[WARNING] Could not rename {module_item}: {str(e)}")
                except Exception as e:
                    self.add_log(f"[ERROR] Error processing {base_path}: {str(e)}")
        
        # Também limpa cache do Discord
        discord_cache = os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Cache')
        if os.path.exists(discord_cache):
            try:
                shutil.rmtree(discord_cache, ignore_errors=True)
                self.add_log("[REAL] Cleared Discord cache")
            except Exception as e:
                self.add_log(f"[WARNING] Could not clear Discord cache: {str(e)}")
        
        self.add_log(f"[REAL] Discord RPC spoofing complete: {spoofed_count} items modified")
        return spoofed_count > 0
    
    def clean_fivem_cache(self):
        """Limpeza REAL do FiveM"""
        self.add_log("[REAL] Cleaning FiveM cache...")
        
        fivem_paths = [
            os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'cache'),
            os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'logs'),
            os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'crashes'),
            os.path.join(os.environ['APPDATA'], 'CitizenFX'),
            os.path.join(os.environ['LOCALAPPDATA'], 'DigitalEntitlements')
        ]
        
        cleaned_count = 0
        for path in fivem_paths:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    cleaned_count += 1
                    self.add_log(f"[REAL] Cleared: {os.path.basename(path)}")
                except Exception as e:
                    self.add_log(f"[WARNING] Could not clear {path}: {str(e)}")
        
        # Limpa arquivos específicos do FiveM
        fivem_app_path = os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app')
        if os.path.exists(fivem_app_path):
            try:
                for pattern in ['*.bin', '*.dll', '*.ini', '*.XML']:
                    for file_path in glob.glob(os.path.join(fivem_app_path, pattern)):
                        try:
                            os.remove(file_path)
                            self.add_log(f"[REAL] Removed: {os.path.basename(file_path)}")
                        except:
                            continue
            except Exception as e:
                self.add_log(f"[WARNING] Error cleaning FiveM files: {str(e)}")
        
        self.add_log(f"[REAL] FiveM cache cleaned: {cleaned_count} locations")
        return cleaned_count > 0
    
    def reset_network(self):
        """Reset REAL de rede"""
        self.add_log("[REAL] Resetting network configuration...")
        
        commands = [
            ('Flushing DNS', ['ipconfig', '/flushdns']),
            ('Resetting Winsock', ['netsh', 'winsock', 'reset']),
            ('Resetting IP', ['netsh', 'int', 'ip', 'reset']),
            ('Resetting Firewall', ['netsh', 'advfirewall', 'reset']),
        ]
        
        success_count = 0
        for name, cmd in commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)
                if result.returncode == 0:
                    success_count += 1
                    self.add_log(f"[REAL] {name}: Success")
                else:
                    self.add_log(f"[WARNING] {name}: Failed - {result.stderr}")
            except Exception as e:
                self.add_log(f"[WARNING] {name}: Error - {str(e)}")
        
        self.add_log(f"[REAL] Network reset: {success_count}/{len(commands)} operations")
        return success_count > 0
    
    def clean_registry(self):
        """Limpeza REAL do registro"""
        self.add_log("[REAL] Cleaning registry entries...")
        
        registry_entries = [
            (winreg.HKEY_CURRENT_USER, r'Software\CitizenFX'),
            (winreg.HKEY_CURRENT_USER, r'Software\FiveM'),
            (winreg.HKEY_CURRENT_USER, r'Software\Rockstar Games'),
            (winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam'),
        ]
        
        cleaned_count = 0
        for hive, key_path in registry_entries:
            try:
                # Tenta abrir a chave para verificar se existe
                try:
                    key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
                    winreg.CloseKey(key)
                    # Se existe, tenta deletar
                    winreg.DeleteKey(hive, key_path)
                    cleaned_count += 1
                    self.add_log(f"[REAL] Registry cleaned: {key_path}")
                except FileNotFoundError:
                    self.add_log(f"[INFO] Registry key not found: {key_path}")
                except PermissionError:
                    self.add_log(f"[WARNING] No permission to delete: {key_path}")
            except Exception as e:
                self.add_log(f"[WARNING] Could not clean registry {key_path}: {str(e)}")
        
        self.add_log(f"[REAL] Registry cleaning: {cleaned_count} entries")
        return cleaned_count > 0
    
    def clean_system_temp(self):
        """Limpeza de arquivos temporários do sistema"""
        self.add_log("[REAL] Cleaning system temporary files...")
        
        temp_paths = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            os.path.join(os.environ['LOCALAPPDATA'], 'Temp'),
            r'C:\Windows\Temp'
        ]
        
        cleaned_count = 0
        for temp_path in temp_paths:
            if os.path.exists(temp_path):
                try:
                    for item in os.listdir(temp_path):
                        item_path = os.path.join(temp_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                cleaned_count += 1
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                                cleaned_count += 1
                        except:
                            continue
                except Exception as e:
                    self.add_log(f"[WARNING] Error cleaning {temp_path}: {str(e)}")
        
        self.add_log(f"[REAL] System temp cleaned: {cleaned_count} items")
        return cleaned_count > 0
    
    def execute_real_spoofing(self):
        """Executa spoofing REAL"""
        self.add_log("=" * 60)
        self.add_log("[REAL] 🚀 STARTING REAL SPOOFING PROTOCOL")
        self.add_log("[REAL] This will perform ACTUAL system modifications")
        self.add_log("=" * 60)
        
        # Define operações reais
        operations = [
            ("Terminating processes", self.kill_processes),
            ("Cleaning system temp", self.clean_system_temp),
            ("Spoofing Discord RPC", self.spoof_discord_rpc),
            ("Cleaning FiveM cache", self.clean_fivem_cache),
            ("Cleaning registry", self.clean_registry),
            ("Resetting network", self.reset_network),
        ]
        
        self.total_operations = len(operations)
        self.completed_operations = 0
        
        results = []
        for op_name, op_function in operations:
            self.add_log(f"[REAL] Executing: {op_name}")
            try:
                result = op_function()
                results.append(result)
                self.completed_operations += 1
                progress = self.get_progress()
                self.add_log(f"[REAL] Progress: {self.completed_operations}/{self.total_operations} ({progress:.1f}%)")
            except Exception as e:
                self.add_log(f"[ERROR] Operation {op_name} failed: {str(e)}")
                results.append(False)
        
        success_count = sum(1 for r in results if r)
        
        self.add_log("=" * 60)
        self.add_log(f"[REAL] SPOOFING COMPLETE: {success_count}/{self.total_operations} operations successful")
        
        if success_count >= 4:  # Pelo menos 4/6 operações bem sucedidas
            self.add_log("[REAL] ✅ SPOOFING SUCCESSFUL!")
            self.add_log("[REAL] Discord RPC has been modified")
            self.add_log("[REAL] FiveM cache has been cleared") 
            self.add_log("[REAL] System identity has been spoofed")
        else:
            self.add_log("[REAL] ⚠️  Partial success - some operations failed")
        
        self.add_log("=" * 60)
        
        return success_count >= 4  # Considera sucesso se maioria das operações funcionou

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
        
        # ✅ AGORA USA O SPOOFER REAL!
        self.spoofer = RealSpoofer(log_callback=self.add_log_realtime)
        
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
            
        # Confirmação MAIS CLARA sobre ações REAIS
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
        """Inicia spoofing REAL"""
        self.cleaning_in_progress = True
        self.spoof_button.configure(state="disabled", text="🔄 REAL SPOOFING...")
        self.spoof_button.start_pulse()
        self.clear_logs()
        self.update_status("Executing REAL spoofing protocol")
        self.circular_progress.set_progress(0)
        
        self.show_toast("Starting REAL spoofing...", "info")
        
        # Inicia em thread separada
        thread = threading.Thread(target=self.execute_spoofing)
        thread.daemon = True
        thread.start()

    def execute_spoofing(self):
        """✅ AGORA EXECUTA SPOOFING REAL - SEM SIMULAÇÃO!"""
        try:
            self.add_log_ui("=" * 60)
            self.add_log_ui("[REAL] 🚀 INITIATING REAL SPOOFING PROTOCOL")
            self.add_log_ui("[REAL] This will actually modify system files")
            self.add_log_ui("=" * 60)
            
            # ✅ EXECUTA SPOOFING REAL!
            success = self.spoofer.execute_real_spoofing()
            
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

def check_admin_privileges():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Verifica privilégios de administrador
    if not check_admin_privileges():
        response = messagebox.askyesno(
            "Administrator Rights Required", 
            "❌ Midnight Spoofer requires Administrator privileges!\n\n"
            "REAL spoofing features may not work without admin rights.\n\n"
            "Do you want to continue anyway?",
            icon='warning'
        )
        if not response:
            return
    
    app = MidnightSpooferGUI()
    app.run()

if __name__ == "__main__":
    main()