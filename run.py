# run.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MidnightSpooferGUI

def check_admin_privileges():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Check administrator privileges
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
    
    # Start the application
    app = MidnightSpooferGUI()
    app.run()

if __name__ == "__main__":
    main()