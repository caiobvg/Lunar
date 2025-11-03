import os
import ctypes
from ctypes import wintypes

class IconManager:
    @staticmethod
    def set_taskbar_icon(root, icon_path):
        """Force set taskbar icon for CustomTkinter windows"""
        try:
            if os.name == 'nt' and os.path.exists(icon_path):
                # Get window handle
                hwnd = ctypes.windll.user32.GetParent(root.winfo_id())

                # Ensure window appears in taskbar
                GWL_EXSTYLE = -20
                WS_EX_APPWINDOW = 0x00040000
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_APPWINDOW)

                # Load icons in different sizes
                ICON_BIG = 1
                ICON_SMALL = 0
                LR_LOADFROMFILE = 0x00000010

                # Load large icon (32x32)
                icon_big = ctypes.windll.user32.LoadImageW(
                    0, icon_path, 1, 32, 32, LR_LOADFROMFILE
                )

                # Load small icon (16x16)
                icon_small = ctypes.windll.user32.LoadImageW(
                    0, icon_path, 1, 16, 16, LR_LOADFROMFILE
                )

                # Set icons
                WM_SETICON = 0x0080
                if icon_big:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, icon_big)
                if icon_small:
                    ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, icon_small)

                return True

        except Exception as e:
            print(f"IconManager error: {e}")

        return False

    @staticmethod
    def set_console_icon():
        """Set icon for console window"""
        try:
            if os.name == 'nt':
                kernel32 = ctypes.windll.kernel32
                console_handle = kernel32.GetConsoleWindow()
                if console_handle:
                    icon_path = 'app.ico'
                    if os.path.exists(icon_path):
                        ICON_BIG = 1
                        LR_LOADFROMFILE = 0x00000010

                        icon_handle = ctypes.windll.user32.LoadImageW(
                            0, icon_path, 1, 32, 32, LR_LOADFROMFILE
                        )

                        if icon_handle:
                            WM_SETICON = 0x0080
                            ctypes.windll.user32.SendMessageW(console_handle, WM_SETICON, ICON_BIG, icon_handle)
        except:
            pass
