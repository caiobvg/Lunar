# src/spoofers/mac_spoofer/select_network.py

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

        # Dry-run toggle
        has_registry = hasattr(self.mac_spoofer, 'registry') and self.mac_spoofer.registry is not None
        initial_dry_run_state = getattr(self.mac_spoofer.registry, 'dry_run', False) if has_registry else False
        self.dry_run_var = ctk.BooleanVar(value=initial_dry_run_state)
        
        dry_run_chk = ctk.CTkCheckBox(self.dialog, text="Dry-run (do not apply changes)", variable=self.dry_run_var)
        dry_run_chk.pack(padx=20, pady=(0,10), anchor="w")
        
        # Disable checkbox if registry is not available
        if not has_registry:
            dry_run_chk.configure(state="disabled")
    
    def select_interface(self, interface):
        self.selected_interface = interface['name']
        self.ok_btn.configure(state="normal")
    
    def confirm(self):
        vendor = self.vendor_var.get()
        self.selected_vendor = vendor if vendor != "Random" else ""

        # Apply dry-run setting to registry checker
        try:
            if hasattr(self.mac_spoofer, 'registry'):
                self.mac_spoofer.registry.set_dry_run(bool(self.dry_run_var.get()))
        except Exception:
            pass

        # Show preview modal with planned registry change
        preview = ctk.CTkToplevel(self.dialog)
        preview.title("Preview Registry Change")
        preview.geometry("380x220")
        preview.transient(self.dialog)
        preview.grab_set()

        iface = next((i for i in self.interfaces if i['name'] == self.selected_interface), None)
        if iface is None:
            preview.destroy()
            self.dialog.destroy()
            return

        # Determine new MAC (preview) without applying
        if self.selected_vendor:
            new_mac = self.mac_spoofer._generate_vendor_mac(self.selected_vendor)
        else:
            new_mac = self.mac_spoofer._generate_random_mac()

        key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\<interface-guid>"

        lbl = ctk.CTkLabel(preview, text=f"Interface: {self.selected_interface}", anchor="w")
        lbl.pack(fill="x", padx=12, pady=(12,4))

        lbl2 = ctk.CTkLabel(preview, text=f"New MAC (preview): {new_mac}", anchor="w")
        lbl2.pack(fill="x", padx=12, pady=4)

        lbl3 = ctk.CTkLabel(preview, text=f"Registry key (target): {key_path}", anchor="w")
        lbl3.pack(fill="x", padx=12, pady=4)

        info = ctk.CTkLabel(preview, text=f"Dry-run: {self.dry_run_var.get()}", anchor="w")
        info.pack(fill="x", padx=12, pady=8)

        btn_frame2 = ctk.CTkFrame(preview)
        btn_frame2.pack(fill="x", padx=12, pady=12)

        cancel = ctk.CTkButton(btn_frame2, text="Cancel", command=lambda: preview.destroy())
        cancel.pack(side="left", expand=True, padx=6)

        apply_btn = ctk.CTkButton(btn_frame2, text="Apply", command=lambda: (preview.destroy(), self.dialog.destroy()))
        apply_btn.pack(side="left", expand=True, padx=6)
    
    def show(self):
        self.dialog.wait_window()
        return self.selected_interface, self.selected_vendor
