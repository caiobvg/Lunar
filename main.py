import os
import sys
import ctypes
import tkinter.messagebox as messagebox

def is_admin():
    """Check if program is running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    # Check if running as admin
    if not is_admin():
        # Request elevation
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    
    # Add src to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Import and execute GUI
    try:
        from gui.main_window import MidnightSpooferGUI
        app = MidnightSpooferGUI()
        app.run()
    except ImportError as e:
        messagebox.showerror("Import Error", 
                           f"Error loading modules:\n{str(e)}\n\n"
                           f"Make sure the folder structure is correct.")
    except Exception as e:
        messagebox.showerror("Error", f"Error starting application:\n{str(e)}")

if __name__ == "__main__":
    main()