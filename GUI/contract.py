import customtkinter as ctk

class ContractTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="Contract", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        ctk.CTkButton(self, text="Add Contract").pack(pady=10)
