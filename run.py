# run.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_admin_privileges():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        print(f"Admin check failed: {e}")
        return False

def main():
    # Check administrator privileges first
    if not check_admin_privileges():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Administrator Rights Required",
                         "❌ Midnight Spoofer requires Administrator privileges!\n\n" +
                         "Please run as Administrator to use all features.\n\n" +
                         "Right-click -> Run as administrator")
        root.destroy()
        return

    # Start with login system
    try:
        from src.auth.login_window import LoginApp
        login_app = LoginApp()
        login_app.run()
    except Exception as e:
        # Fallback error handling
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
