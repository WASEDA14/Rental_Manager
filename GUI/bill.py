import customtkinter as ctk

class BillTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="BILLS", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        ctk.CTkButton(self, text="Add Room").pack(pady=10)
