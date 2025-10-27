import customtkinter as ctk
import time

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