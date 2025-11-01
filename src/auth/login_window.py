import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from .auth_system_firebase import AuthSystemFirebase
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class LoginApp:
    def __init__(self):
        self.auth = AuthSystemFirebase()
        self.current_user = None
        self.setup_login_window()

    def setup_login_window(self):
        """Initialize the main login window"""
        self.window = ctk.CTk()
        self.window.title("Midnight Spoofer - Login")
        self.window.geometry("450x600")
        self.window.resizable(False, False)

        # Center window
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # Theme setup
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.create_login_frame()

    def create_login_frame(self):
        """Create the main login interface"""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.main_frame.pack(pady=40, padx=40, fill="both", expand=True)

        # Logo/Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="🚀 MIDNIGHT SPOOFER",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#6b21ff"
        )
        title.pack(pady=30)

        # Subtitle
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Advanced System Identity Protection",
            font=ctk.CTkFont(size=12),
            text_color="#b0b0ff"
        )
        subtitle.pack(pady=(0, 30))

        # Login form container
        self.login_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.login_container.pack(fill="both", expand=True, padx=20)

        # Username field
        self.username_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Email",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(pady=10)

        # Password field
        self.password_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Password",
            show="•",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=10)

        # Login button
        login_btn = ctk.CTkButton(
            self.login_container,
            text="LOGIN",
            command=self.login,
            width=300,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#6b21ff",
            hover_color="#4a1c6d"
        )
        login_btn.pack(pady=15)

        # Create Account button
        create_btn = ctk.CTkButton(
            self.login_container,
            text="CREATE ACCOUNT",
            command=self.show_license_activation,
            width=300,
            height=45,
            fg_color="transparent",
            border_width=2,
            border_color="#6b21ff",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#6b21ff"
        )
        create_btn.pack(pady=15)

        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.login())

    def show_register(self):
        """Show registration dialog"""
        # Hide main login
        self.main_frame.pack_forget()

        # Create registration frame
        self.register_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.register_frame.pack(pady=40, padx=40, fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(
            self.register_frame,
            text="CREATE NEW ACCOUNT",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#6b21ff"
        )
        title.pack(pady=20)

        # Form container
        form_frame = ctk.CTkFrame(self.register_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Registration fields
        self.reg_entries = {}

        fields = [
            ("Username", "username"),
            ("Email", "email"),
            ("Password", "password"),
            ("Confirm Password", "confirm_password"),
            ("License Key", "license_key")
        ]

        for label, key in fields:
            entry = ctk.CTkEntry(
                form_frame,
                placeholder_text=label,
                show="•" if "password" in key else "",
                width=300,
                height=40,
                font=ctk.CTkFont(size=12)
            )
            entry.pack(pady=8)
            self.reg_entries[key] = entry

        # Register button
        register_btn = ctk.CTkButton(
            form_frame,
            text="REGISTER",
            command=self.register,
            width=300,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00ff88",
            hover_color="#00cc66"
        )
        register_btn.pack(pady=20)

        # Back button
        back_btn = ctk.CTkButton(
            form_frame,
            text="← BACK TO LOGIN",
            command=self.show_login,
            width=300,
            height=35,
            fg_color="transparent",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        back_btn.pack(pady=5)

    def show_license_activation(self):
        """Show license activation dialog for account creation"""
        # Hide main login
        self.main_frame.pack_forget()

        # Create license frame
        self.license_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.license_frame.pack(pady=40, padx=40, fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(
            self.license_frame,
            text="ENTER LICENSE KEY",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#6b21ff"
        )
        title.pack(pady=30)

        # Description
        desc = ctk.CTkLabel(
            self.license_frame,
            text="Enter your license key to create an account",
            font=ctk.CTkFont(size=12),
            text_color="#b0b0ff"
        )
        desc.pack(pady=(0, 20))

        # License key entry
        self.license_entry = ctk.CTkEntry(
            self.license_frame,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            width=300,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="center"
        )
        self.license_entry.pack(pady=20)

        # Next button
        next_btn = ctk.CTkButton(
            self.license_frame,
            text="NEXT",
            command=self.validate_license_and_show_register,
            width=300,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#00ff88",
            hover_color="#00cc66"
        )
        next_btn.pack(pady=20)

        # Back button
        back_btn = ctk.CTkButton(
            self.license_frame,
            text="← BACK",
            command=self.show_login,
            width=300,
            height=35,
            fg_color="transparent",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        back_btn.pack(pady=10)

    def show_login(self):
        """Return to login screen - CORRIGIDO"""
        try:
            # Hide other frames
            if hasattr(self, 'register_frame') and self.register_frame:
                self.register_frame.pack_forget()
                self.register_frame.destroy()
                delattr(self, 'register_frame')

            if hasattr(self, 'license_frame') and self.license_frame:
                self.license_frame.pack_forget()
                self.license_frame.destroy()
                delattr(self, 'license_frame')

            # Clear any stored license
            if hasattr(self, 'validated_license'):
                delattr(self, 'validated_license')

            # Ensure main login frame is visible
            if hasattr(self, 'main_frame'):
                self.main_frame.pack(pady=40, padx=40, fill="both", expand=True)

        except Exception as e:
            print(f"Error in show_login: {e}")
            # Fallback: recriar a interface completa se necessário
            self.setup_login_window()

    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        if self.auth.verify_login(username, password):
            self.current_user = username
            self.window.destroy()
            # Start main application
            self.start_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def register(self):
        """Handle user registration - CORRIGIDO"""
        data = {}
        for key, entry in self.reg_entries.items():
            data[key] = entry.get().strip()

        # Validation
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required")
            return

        if data['password'] != data['confirm_password']:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(data['password']) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        if not self.auth.validate_license(data['license_key']):
            messagebox.showerror("Error", "Invalid or already used license key")
            return

        # Attempt registration
        if self.auth.register_user(data['username'], data['email'], data['password'], data['license_key']):
            messagebox.showinfo("Success", "Account created successfully! Please login.")

            # CORREÇÃO: Redirecionar para login e preencher email
            self.show_login()
            self.username_entry.delete(0, 'end')
            self.username_entry.insert(0, data['email'])
            self.password_entry.focus_set()

        else:
            messagebox.showerror("Error", "Username, email, or license key already exists")

    def validate_license_and_show_register(self):
        """Validate license key and show registration form"""
        license_key = self.license_entry.get().strip()

        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return

        if self.auth.validate_license(license_key):
            # Store the validated license key
            self.validated_license = license_key
            # Show registration form
            self.show_register_from_license()
        else:
            messagebox.showerror("Error", "License key is invalid or already in use")

    def show_register_from_license(self):
        """Show registration form after license validation"""
        # Hide license frame
        self.license_frame.pack_forget()

        # Create registration frame
        self.register_frame = ctk.CTkFrame(self.window, corner_radius=15)
        self.register_frame.pack(pady=40, padx=40, fill="both", expand=True)

        # Title
        title = ctk.CTkLabel(
            self.register_frame,
            text="CREATE YOUR ACCOUNT",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#6b21ff"
        )
        title.pack(pady=20)

        # Form container
        form_frame = ctk.CTkFrame(self.register_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Registration fields (without license key since it's already validated)
        self.reg_entries = {}

        fields = [
            ("Username", "username"),
            ("Email", "email"),
            ("Password", "password"),
            ("Confirm Password", "confirm_password")
        ]

        for label, key in fields:
            entry = ctk.CTkEntry(
                form_frame,
                placeholder_text=label,
                show="•" if "password" in key else "",
                width=300,
                height=40,
                font=ctk.CTkFont(size=12)
            )
            entry.pack(pady=8)
            self.reg_entries[key] = entry

        # Register button
        register_btn = ctk.CTkButton(
            form_frame,
            text="CREATE ACCOUNT",
            command=self.register_with_validated_license,
            width=300,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00ff88",
            hover_color="#00cc66"
        )
        register_btn.pack(pady=20)

        # Back button
        back_btn = ctk.CTkButton(
            form_frame,
            text="← BACK",
            command=self.show_license_activation,
            width=300,
            height=35,
            fg_color="transparent",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        back_btn.pack(pady=5)

    def register_with_validated_license(self):
        """Handle registration with pre-validated license - CORRIGIDO"""
        data = {}
        for key, entry in self.reg_entries.items():
            data[key] = entry.get().strip()

        # Validation
        if not all(data.values()):
            messagebox.showerror("Error", "All fields are required")
            return

        if data['password'] != data['confirm_password']:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if len(data['password']) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return

        # Use the pre-validated license key
        license_key = self.validated_license

        # DEBUG: Verificar existência antes de registrar
        print("=== DEBUG REGISTRO ===")
        print(f"Username: {data['username']}")
        print(f"Email: {data['email']}")
        print(f"License: {license_key}")

        # Verifica existência antes de registrar
        check_result = self.auth.check_user_exists(data['username'], data['email'])
        print(f"Check result: {check_result}")

        # Attempt registration
        success = self.auth.register_user(data['username'], data['email'], data['password'], license_key)
        print(f"Resultado registro: {success}")

        if success:
            messagebox.showinfo("Success", "Account created successfully! You can now login.")

            # CORREÇÃO: Redirecionar para login e preencher email
            self.show_login()
            self.username_entry.delete(0, 'end')
            self.username_entry.insert(0, data['email'])
            self.password_entry.focus_set()

        else:
            # Mensagem mais específica baseada na verificação
            if check_result['email_exists'] and check_result['username_exists']:
                error_msg = "Both email and username are already registered"
            elif check_result['email_exists']:
                error_msg = "Email is already registered"
            elif check_result['username_exists']:
                error_msg = "Username is already taken"
            else:
                error_msg = "Unable to create account. Possible reasons:\n" \
                           "• Email already registered\n" \
                           "• Username already taken\n" \
                           "• License key already used\n" \
                           "• Network connection issue"

            messagebox.showerror("Registration Failed", error_msg)

    def activate_license(self):
        """Handle license activation (legacy method)"""
        license_key = self.license_entry.get().strip()

        if not license_key:
            messagebox.showerror("Error", "Please enter a license key")
            return

        if self.auth.validate_license(license_key):
            messagebox.showinfo("Success", "License is valid and available for registration")
        else:
            messagebox.showerror("Error", "License key is invalid or already in use")

    def start_main_app(self):
        """Start the main Midnight Spoofer application"""
        try:
            from dashboard.dashboard import MidnightSpooferGUI
            from controllers.spoofer_controller import SpoofingController
            from cleaners.system_cleaner import SystemCleaner
            from utils.hardware_reader import HardwareReader
            from utils.logger import logger
            from spoofers.mac_spoofer.mac_spoofer import MACSpoofer
            from spoofers.hwid_spoofer.hwid_spoofer import HWIDSpoofer
            from spoofers.guid_spoofer.guid_spoofer import GUIDSpoofer

            # Initialize all core components
            cleaner = SystemCleaner()
            hw_reader = HardwareReader()
            mac_spoofer = MACSpoofer()
            hwid_spoofer = HWIDSpoofer()
            guid_spoofer = GUIDSpoofer()

            # Initialize controller
            spoofer_controller = SpoofingController(
                cleaner=cleaner,
                mac_spoofer=mac_spoofer,
                hwid_spoofer=hwid_spoofer,
                guid_spoofer=guid_spoofer,
                hw_reader=hw_reader
            )

            # Start main GUI
            app = MidnightSpooferGUI(spoofer_controller)
            app.run()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start main application: {str(e)}")
            sys.exit(1)

    def run(self):
        """Start the login application"""
        self.window.mainloop()
