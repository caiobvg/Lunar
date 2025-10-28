# src/spoofers/mac_spoofer/select_network.py

import customtkinter as ctk

class InterfaceSelectionDialog:
    def __init__(self, parent, mac_spoofer):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Select Network Interface")
        self.dialog.geometry("450x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(fg_color="#1a1a1a")
        
        self.mac_spoofer = mac_spoofer
        self.selected_interface = None
        self.selected_vendor = None
        self.new_mac = None
        self.interface_buttons = []

        self.setup_ui()

    def setup_ui(self):
        # --- Fontes ---
        TITLE_FONT = ctk.CTkFont(family="Roboto", size=20, weight="bold")
        BODY_FONT = ctk.CTkFont(family="Roboto", size=12)
        BUTTON_FONT = ctk.CTkFont(family="Roboto", size=12, weight="bold")

        # --- Frame Principal ---
        main_frame = ctk.CTkFrame(self.dialog, fg_color="#1a1a1a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Título ---
        title = ctk.CTkLabel(
            main_frame,
            text="Select Network Interface",
            font=TITLE_FONT,
            text_color="#ffffff"
        )
        title.pack(pady=(0, 20))

        # --- Lista de Interfaces ---
        interfaces_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="#2a2a2a",
            border_width=1,
            border_color="#6a0dad"
        )
        interfaces_frame.pack(fill="both", expand=True, pady=10)

        self.interfaces = self.mac_spoofer.get_interfaces()

        for iface in self.interfaces:
            btn = ctk.CTkButton(
                interfaces_frame,
                text=f"{iface['description']}\nMAC: {iface['mac_address']}",
                height=60,
                font=BODY_FONT,
                fg_color="#2a2a2a",
                border_width=2,
                border_color="#2a2a2a",
                hover_color="#5a1f99",
                text_color="#ffffff",
                corner_radius=10
            )
            btn.configure(command=lambda i=iface, b=btn: self.select_interface(i, b))
            btn.pack(fill="x", pady=8, padx=10)
            self.interface_buttons.append(btn)

        # --- Seleção de Vendor ---
        vendor_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        vendor_frame.pack(fill="x", pady=10)

        vendor_label = ctk.CTkLabel(
            vendor_frame,
            text="Select Vendor (Optional):",
            font=BODY_FONT,
            text_color="#ffffff"
        )
        vendor_label.pack(anchor="w", pady=(0, 5))

        vendors = ["Random"] + list(self.mac_spoofer.VENDOR_OUI.keys())
        self.vendor_var = ctk.StringVar(value="Random")

        vendor_menu = ctk.CTkOptionMenu(
            vendor_frame,
            values=vendors,
            variable=self.vendor_var,
            font=BUTTON_FONT,
            fg_color="#6a0dad",
            button_color="#6a0dad",
            button_hover_color="#8a2be2",
            dropdown_fg_color="#2a2a2a",
            dropdown_hover_color="#8a2be2",
            dropdown_text_color="#ffffff",
            text_color="#ffffff",
            corner_radius=8,
            height=40
        )
        vendor_menu.pack(fill="x", expand=True)

        # --- Botões de Ação ---
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=BUTTON_FONT,
            fg_color="#3a3a3a",
            hover_color="#4a4a4a",
            height=40,
            corner_radius=8
        )
        cancel_btn.pack(side="left", expand=True, padx=(0, 10))

        self.ok_btn = ctk.CTkButton(
            btn_frame,
            text="OK",
            command=self.confirm,
            state="disabled",
            font=BUTTON_FONT,
            fg_color="#6a0dad",
            hover_color="#8a2be2",
            height=40,
            corner_radius=8
        )
        self.ok_btn.pack(side="left", expand=True, padx=(10, 0))

    def select_interface(self, interface, selected_button):
        self.selected_interface = interface['name']

        for btn in self.interface_buttons:
            if btn == selected_button:
                btn.configure(border_color="#8a2be2", fg_color="#8a2be2", hover_color="#8a2be2")
            else:
                btn.configure(border_color="#2a2a2a", fg_color="#2a2a2a", hover_color="#5a1f99")

        self.ok_btn.configure(state="normal")
    
    def confirm(self):
        vendor = self.vendor_var.get()
        self.selected_vendor = vendor if vendor != "Random" else ""

        # Janela de preview (mantida a lógica, mas pode ser estilizada no futuro)
        preview = ctk.CTkToplevel(self.dialog)
        preview.title("Preview Registry Change")
        preview.geometry("400x250")
        preview.transient(self.dialog)
        preview.grab_set()
        preview.configure(fg_color="#1a1a1a")

        iface = next((i for i in self.interfaces if i['name'] == self.selected_interface), None)
        if iface is None:
            preview.destroy()
            self.dialog.destroy()
            return

        if self.selected_vendor:
            self.new_mac = self.mac_spoofer._generate_vendor_mac(self.selected_vendor)
        else:
            self.new_mac = self.mac_spoofer._generate_random_mac()

        key_path = f"SYSTEM\\...\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\<GUID>"

        ctk.CTkLabel(preview, text=f"Interface: {self.selected_interface}", anchor="w", text_color="#ffffff").pack(fill="x", padx=15, pady=(15, 5))
        ctk.CTkLabel(preview, text=f"New MAC (Preview): {self.new_mac}", anchor="w", text_color="#ffffff").pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(preview, text=f"Registry Key (Target): {key_path}", anchor="w", wraplength=370, text_color="#ffffff").pack(fill="x", padx=15, pady=5)

        btn_frame2 = ctk.CTkFrame(preview, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=15, pady=20)

        cancel = ctk.CTkButton(btn_frame2, text="Cancel", command=preview.destroy, fg_color="#3a3a3a", hover_color="#4a4a4a")
        cancel.pack(side="left", expand=True, padx=(0, 5))

        apply_btn = ctk.CTkButton(btn_frame2, text="Apply", command=lambda: (preview.destroy(), self.dialog.destroy()), fg_color="#6a0dad", hover_color="#8a2be2")
        apply_btn.pack(side="left", expand=True, padx=(5, 0))
    
    def show(self):
        self.dialog.wait_window()
        return self.selected_interface, self.selected_vendor, self.new_mac
