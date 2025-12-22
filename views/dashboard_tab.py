import customtkinter as ctk
from tkinter import messagebox

class Card(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str, color: str):
        super().__init__(parent, corner_radius=12)
        self.configure(fg_color=color)
        self._value = value
        self._title = title
        self._color = color
        
        # Store widgets for later updates
        self.value_label = None
        self.title_label = None

        self.setup_ui()
    
    def setup_ui(self):
        # Configure layout
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Value (big number)
        self.value_label = ctk.CTkLabel(
            self, 
            text=self._value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        self.value_label.grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self, 
            text=self._title, 
            text_color="white"
        )
        self.title_label.grid(row=1, column=0, padx=16, sticky="w")
    
    def update_value(self, new_value):
        """Update the value displayed in the card"""
        self.value_label.configure(text=new_value)
    
    def update_title(self, new_title):
        """Update the title of the card"""
        self.title_label.configure(text=new_title)

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        if self.controller is not None:
            self.controller.view = self

        self.setup_ui()

        if self.controller is not None:
            self.refresh_data()

    def setup_ui(self):
        # Header
        ctk.CTkLabel(
            self, 
            text="Have a nice day", 
            font=ctk.CTkFont(size=40, weight="bold")
        ).pack(pady='30')
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            self,
            text="⟳ Refresh",
            command=self.refresh_data,
            width=100,
            fg_color="#2c3e50",
            hover_color="#34495e"
        )
        refresh_btn.pack(anchor='e', padx=16)
        
        # Row containing the cards
        self.cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cards_frame.pack(fill="x", padx=16, pady=16)
        
        # Configure 3 equal columns
        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")
        
        # Create cards
        self.room_card = Card(self.cards_frame, "Rooms", "0/0", "#3498db")
        self.tenant_card = Card(self.cards_frame, "Tenants", "0", "#f1c40f")
        self.payment_card = Card(self.cards_frame, "Payments This Month", "0.0", "#27ae60")
        
        # Place cards in grid
        self.room_card.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.tenant_card.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.payment_card.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
    
    def refresh_data(self):
        """Request a refresh of the dashboard data"""
        if self.controller is None:
            return
        self.controller.refresh_data()
    
    def update_room_card(self, occupied, total):
        """Update the room card with new data"""
        self.room_card.update_value(f"{occupied}/{total}")
    
    def update_tenant_card(self, count):
        """Update the tenant card with new data"""
        self.tenant_card.update_value(str(count))
    
    def update_payment_card(self, amount):
        """Update the payment card with new data"""
        # Format as currency (you might want to add a currency formatter)
        formatted_amount = f"{amount:,.0f} VND" if amount is not None else "0 VND"
        self.payment_card.update_value(formatted_amount)
