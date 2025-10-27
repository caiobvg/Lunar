import customtkinter as ctk

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_fg_color = self.cget("fg_color")
        self.hover_fg_color = "#4a1c6d"
        self.animation_running = False
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        
    def on_enter(self, event):
        self.configure(fg_color=self.hover_fg_color)
        
    def on_leave(self, event):
        if not self.animation_running:
            self.configure(fg_color=self.default_fg_color)
    
    def start_pulse(self):
        self.animation_running = True
        self._pulse_animation()
    
    def stop_pulse(self):
        self.animation_running = False
        self.configure(fg_color=self.default_fg_color)
    
    def _pulse_animation(self):
        if not self.animation_running:
            return
            
        colors = ["#2d1152", "#3a1668", "#471c7e", "#542194", "#6127aa"]
        current = 0
        
        def update_color():
            nonlocal current
            if self.animation_running:
                self.configure(fg_color=colors[current])
                current = (current + 1) % len(colors)
                self.after(200, update_color)
        
        update_color()