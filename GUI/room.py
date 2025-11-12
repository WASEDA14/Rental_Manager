import customtkinter as ctk

class RoomTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        ctk.CTkLabel(self, text="ROOMS", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        ctk.CTkButton(self, text="Add Room").pack(pady=10)
