# src/gui/components/progress.py

import customtkinter as ctk

class CircularProgress(ctk.CTkCanvas):
    def __init__(self, parent, size=200, **kwargs):
        super().__init__(parent, width=size, height=size, **kwargs)
        self.size = size
        self.center = size // 2
        self.radius = size // 2 - 10
        self.progress = 0
        
        self.configure(bg="#0a0a1a", highlightthickness=0)
        self.draw_background()
        self.draw_progress()
    
    def draw_background(self):
        self.create_oval(10, 10, self.size-10, self.size-10, 
                        outline="#1a1a2e", width=8, fill="#0a0a1a")
    
    def draw_progress(self):
        self.delete("progress")
        angle = 360 * self.progress / 100
        
        self.create_arc(10, 10, self.size-10, self.size-10,
                       start=90, extent=-angle,
                       outline="#6b21ff", width=8, style="arc", tags="progress")
        
        # Progress text
        self.create_text(self.center, self.center, text=f"{int(self.progress)}%",
                        fill="white", font=("Segoe UI", 20, "bold"), tags="progress")
    
    def set_progress(self, value):
        self.progress = max(0, min(100, value))
        self.draw_progress()