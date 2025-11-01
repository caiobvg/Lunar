# test_icons.py
import os
import tkinter as tk
from tkinter import messagebox

def test_icons():
    print("Testing icon files...")

    icon_files = ['app.ico', 'app.png']

    for icon_file in icon_files:
        if os.path.exists(icon_file):
            print(f"[OK] {icon_file} found")
        else:
            print(f"[MISSING] {icon_file} missing")

    # Test window with icon
    try:
        root = tk.Tk()
        root.withdraw()

        if os.path.exists('app.ico'):
            root.iconbitmap('app.ico')
            print("[OK] Icon loaded successfully in test window")
        else:
            print("[ERROR] Could not load icon in test window")

        root.destroy()
    except Exception as e:
        print(f"[ERROR] Icon test failed: {e}")

if __name__ == "__main__":
    test_icons()
