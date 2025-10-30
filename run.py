# run.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dashboard.dashboard import MidnightSpooferGUI
from src.controllers.spoofer_controller import SpoofingController
from src.cleaners.system_cleaner import SystemCleaner
from src.utils.hardware_reader import HardwareReader
from src.utils.logger import logger
from src.spoofers.mac_spoofer.mac_spoofer import MACSpoofer
from src.spoofers.hwid_spoofer.hwid_spoofer import HWIDSpoofer
from src.spoofers.guid_spoofer.guid_spoofer import GUIDSpoofer

def check_admin_privileges():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logger.log_error(f"Admin check failed: {e}", "SYSTEM")
        return False

def main():
    # Check administrator privileges
    if not check_admin_privileges():
        messagebox.showerror("Administrator Rights Required", 
                         "❌ Midnight Spoofer requires Administrator privileges!\n\n" +
                         "Please run as Administrator to use all features.\n\n" +
                         "Right-click -> Run as administrator")
        return
    
    # 1. Initialize all core components (dependencies)
    try:
        cleaner = SystemCleaner()
        hw_reader = HardwareReader()
        mac_spoofer = MACSpoofer()
        hwid_spoofer = HWIDSpoofer()
        guid_spoofer = GUIDSpoofer()
        logger.log_info("Core components initialized successfully", "SYSTEM")
    except Exception as e:
        logger.log_error(f"Fatal error during component initialization: {e}", "CRITICAL")
        messagebox.showerror("Initialization Error", f"A critical error occurred: {e}")
        return

    # 2. Initialize the controller with the components
    # The controller will now manage the logic, but the UI will trigger it.
    # Callbacks are still needed for the controller to update the UI.
    # We will define them inside the GUI class and pass them later.
    spoofer_controller = SpoofingController(
        cleaner=cleaner,
        mac_spoofer=mac_spoofer,
        hwid_spoofer=hwid_spoofer,
        guid_spoofer=guid_spoofer,
        hw_reader=hw_reader
    )

    # 3. Start the application, passing the controller to the GUI
    app = MidnightSpooferGUI(spoofer_controller)
    app.run()

if __name__ == "__main__":
    main()
