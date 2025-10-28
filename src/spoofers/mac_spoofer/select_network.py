import customtkinter as ctk

class InterfaceSelectionDialog:
    def __init__(self, parent, mac_spoofer):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Select Network Interface")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.mac_spoofer = mac_spoofer
        self.selected_interface = None
        self.selected_vendor = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = ctk.CTkLabel(
            self.dialog,
            text="Select Network Interface",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=20)
        
        # Interfaces List
        interfaces_frame = ctk.CTkFrame(self.dialog)
        interfaces_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get network interfaces
        self.interfaces = self.mac_spoofer.get_interfaces()
        
        for iface in self.interfaces:
            btn = ctk.CTkButton(
                interfaces_frame,
                text=f"{iface['description']}\nMAC: {iface['mac_address']}",
                command=lambda i=iface: self.select_interface(i),
                height=60,
                fg_color="#1a1a2e",
                hover_color="#2d1152"
            )
            btn.pack(fill="x", pady=5)
        
        # Vendor Selection
        vendor_frame = ctk.CTkFrame(self.dialog)
        vendor_frame.pack(fill="x", padx=20, pady=10)
        
        vendor_label = ctk.CTkLabel(vendor_frame, text="Select Vendor (Optional):")
        vendor_label.pack(anchor="w", pady=5)
        
        vendors = ["Random"] + list(self.mac_spoofer.VENDOR_OUI.keys())
        self.vendor_var = ctk.StringVar(value="Random")
        
        vendor_menu = ctk.CTkOptionMenu(
            vendor_frame,
            values=vendors,
            variable=self.vendor_var
        )
        vendor_menu.pack(fill="x")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a"
        )
        cancel_btn.pack(side="left", expand=True, padx=5)
        
        self.ok_btn = ctk.CTkButton(
            btn_frame,
            text="OK",
            command=self.confirm,
            state="disabled",
            fg_color="#2d1152",
            hover_color="#4a1c6d"
        )
        self.ok_btn.pack(side="left", expand=True, padx=5)
    
    def select_interface(self, interface):
        self.selected_interface = interface['name']
        self.ok_btn.configure(state="normal")
    
    def confirm(self):
        vendor = self.vendor_var.get()
        self.selected_vendor = vendor if vendor != "Random" else ""
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.selected_interface, self.selected_vendor
