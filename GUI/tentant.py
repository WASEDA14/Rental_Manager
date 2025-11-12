import customtkinter as ctk

class TenantTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Tentant", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        ctk.CTkButton(self, text="Add Tentant").pack(pady=10)
