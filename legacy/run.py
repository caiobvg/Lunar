# run.py
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import sys
import os
from src.auth.auth_system_firebase import AuthSystemFirebase as AuthSystem

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

def get_icon_path():
    """Get absolute path to icon files"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Try different icon locations
    icon_locations = [
        os.path.join(base_dir, 'app.ico'),
        os.path.join(base_dir, 'src', 'assets', 'app.ico'),
        os.path.join(base_dir, 'assets', 'app.ico'),
    ]

    for icon_path in icon_locations:
        if os.path.exists(icon_path):
            return icon_path

    return None

def set_window_icon(window, icon_path=None):
    """Set window icon with multiple fallback methods"""
    if icon_path is None:
        icon_path = get_icon_path()

    if not icon_path or not os.path.exists(icon_path):
        print("Icon file not found")
        return False

    try:
        # Method 1: Standard iconbitmap
        window.iconbitmap(icon_path)
        return True
    except Exception as e:
        print(f"Method 1 failed: {e}")

    try:
        # Method 2: Use PhotoImage for PNG fallback
        if icon_path.endswith('.png'):
            icon_image = tk.PhotoImage(file=icon_path)
            window.iconphoto(True, icon_image)
            return True
    except Exception as e:
        print(f"Method 2 failed: {e}")

    try:
        # Method 3: Windows API for taskbar
        if os.name == 'nt':
            import ctypes
            from ctypes import wintypes

            # Get window handle
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

            # Load icon
            ICON_BIG = 1
            LR_LOADFROMFILE = 0x00000010

            icon_handle = ctypes.windll.user32.LoadImageW(
                0, icon_path, 1, 0, 0, LR_LOADFROMFILE
            )

            if icon_handle:
                WM_SETICON = 0x0080
                ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, icon_handle)
                return True
    except Exception as e:
        print(f"Method 3 failed: {e}")

    return False

def main():
    # Check administrator privileges first
    if not check_admin_privileges():
        root = tk.Tk()
        root.withdraw()

        # Set icon for error dialog
        icon_path = get_icon_path()
        if icon_path:
            try:
                root.iconbitmap(icon_path)
            except:
                pass

        messagebox.showerror("Administrator Rights Required",
                         "❌ Midnight Spoofer requires Administrator privileges!\n\n" +
                         "Please run as Administrator to use all features.\n\n" +
                         "Right-click -> Run as administrator")
        root.destroy()
        return

    # Start with login system
    try:
        from src.auth.login_window import LoginApp

        # Get icon path and pass to LoginApp
        icon_path = get_icon_path()
        login_app = LoginApp(icon_path=icon_path)
        login_app.run()
    except Exception as e:
        # Fallback error handling
        root = tk.Tk()
        root.withdraw()

        # Try to set icon
        icon_path = get_icon_path()
        if icon_path:
            try:
                root.iconbitmap(icon_path)
            except:
                pass

        messagebox.showerror("Startup Error", f"Failed to start application: {str(e)}")
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()
