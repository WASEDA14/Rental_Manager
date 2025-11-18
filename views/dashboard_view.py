import customtkinter as ctk

class Card(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str, color: str, view_text="View"):
        super().__init__(parent, corner_radius=12)
        self.configure(fg_color=color)

        # layout trong card
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # số lớn
        ctk.CTkLabel(self, text=value,
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="white").grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")
        # tiêu đề
        ctk.CTkLabel(self, text=title, text_color="white").grid(row=1, column=0, padx=16, sticky="w")
        # nút view
        ctk.CTkButton(self, text=view_text, height=30,
                      fg_color="white", text_color="black",
                      hover_color="#e6e6e6").grid(row=3, column=0, padx=16, pady=16, sticky="w")


class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        ctk.CTkLabel(self, text="Have a nice day", font=ctk.CTkFont(size=24, weight="bold")).pack(pady='30')
        # hàng chứa 3 card
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=16)

        # 3 cột giãn đều
        for i in range(3):
            row.grid_columnconfigure(i, weight=1, uniform="cards")

        Card(row, "Room",  "10/20",   "#3498db").grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        Card(row, "Tenants", "10",   "#f1c40f").grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        Card(row, "Payments This Month", "0.0", "#27ae60").grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
