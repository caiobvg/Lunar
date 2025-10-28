# run.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dashboard.dashboard import MidnightSpooferGUI

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
        messagebox.showerror("Administrator Rights Required", 
                         "❌ Midnight Spoofer requires Administrator privileges!\n\n" +
                         "Please run as Administrator to use all features.\n\n" +
                         "Right-click -> Run as administrator")
        return
    
    # Start the application
    app = MidnightSpooferGUI()
    app.run()

if __name__ == "__main__":
    main()
