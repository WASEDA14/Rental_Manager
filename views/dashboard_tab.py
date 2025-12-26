from tkinter import messagebox

import customtkinter as ctk
from views.bill_tab import billTab
from views.contract_tab import contractTab
from views.room_tab import roomTab
from views.tenant_tab import tenantTab
from views.report_tab import ReportTab

class Card(ctk.CTkFrame):
    def __init__(self, parent, title: str, value: str, color: str):
        super().__init__(parent, corner_radius=12)
        self.configure(fg_color=color)
        self._value = value
        self._title = title

        self.value_label = ctk.CTkLabel(
            self, text=self._value, font=ctk.CTkFont(size=28, weight="bold"), text_color="white"
        )
        self.value_label.grid(row=0, column=0, padx=16, pady=(16, 4), sticky="w")

        self.title_label = ctk.CTkLabel(self, text=self._title, text_color="white")
        self.title_label.grid(row=1, column=0, padx=16, sticky="w")

    def update_value(self, new_value):
        self.value_label.configure(text=new_value)


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller=None, login_window=None):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.controller = controller
        self.active_button = None
        self.tabs = {}
        self.nav_buttons = []
        self.setup_ui()
        self.login_window = login_window

        if self.controller:
            self.controller.view = self

    def setup_ui(self):
        self.setup_sidebar()
        self.setup_content()
        self.show_dashboard()

    def setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0,fg_color=("#f0f2f5", "#1a1a1a"), border_width=1, border_color=("#e0e0e0", "#2d2d2d"))
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(sidebar_content, text="Rental Manager",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=("#2b2b2b", "#ffffff")).pack(pady=(10, 20))

        nav_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        nav_frame.pack(fill="x")

        self.nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Room", self.show_room),
            ("Tenant", self.show_tenant),
            ("Contract", self.show_contract),
            ("Bill", self.show_bill),
            ("Report", self.show_report)
        ]

        # First pass: create all buttons
        for text, command in self.nav_buttons:
            btn = ctk.CTkButton(
                nav_frame, 
                text=text, 
                command=lambda t=text, c=command: self.on_nav_button_click(t, c),
                anchor="w", 
                height=40, 
                corner_radius=8,
                font=ctk.CTkFont(weight="normal"),
                fg_color=("#ffffff", "#2b2b2b"),
                text_color=("#2b2b2b", "#ffffff"),
                hover_color=("#e9e9e9", "#3a3a3a"),
                border_width=1, 
                border_color=("#e0e0e0", "#3a3a3a")
            )
            btn.pack(fill="x", pady=4)
            setattr(self, f"{text.lower()}_button", btn)
        
        # Set Dashboard as active after all buttons are created
        if hasattr(self, 'dashboard_button'):
            self.set_active_button(self.dashboard_button)

        # Logout
        logout_frame = ctk.CTkFrame(sidebar_content, fg_color="transparent")
        logout_frame.pack(fill="x", side="bottom")
        ctk.CTkButton(logout_frame, text="Logout", command=self.log_out,
                       height=40, corner_radius=8,
                       font=ctk.CTkFont(weight="bold"),
                       fg_color=("#e74c3c", "#c0392b"),
                       hover_color=("#c0392b", "#e74c3c"),
                       text_color=("#ffffff", "#ffffff")).pack(fill="x", pady=(10, 0))

    def setup_content(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="right", fill="both", expand=True)

        # Dashboard frame
        self.dashboard_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.dashboard_frame, text="Dashboard",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 20))

        self.cards_frame = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 20), anchor="center")

        for i in range(3):
            self.cards_frame.grid_columnconfigure(i, weight=1, uniform="cards")

        self.room_card = Card(self.cards_frame, "Rooms", "0/0", "#3498db")
        self.tenant_card = Card(self.cards_frame, "Tenants", "0", "#f1c40f")
        self.payment_card = Card(self.cards_frame, "Payments", "0/0", "#27ae60")


        self.room_card.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.tenant_card.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        self.payment_card.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

    def lazy_load_tab(self, name, cls, user_id=None):
        if name not in self.tabs:
            if name == "report":
                # For ReportTab, we always need to pass user_id, even if it's None
                self.tabs[name] = cls(self.content, user_id)
            else:
                # For other tabs, use the standard initialization
                self.tabs[name] = cls(self.content)
        return self.tabs[name]

    def hide_all(self):
        self.dashboard_frame.pack_forget()
        for tab in self.tabs.values():
            tab.pack_forget()

    def on_nav_button_click(self, button_text, command):
        button = getattr(self, f"{button_text.lower()}_button")
        self.set_active_button(button)
        command()
        
    def set_active_button(self, button):
        for text, _ in self.nav_buttons:
            btn = getattr(self, f"{text.lower()}_button")
            btn.configure(
                fg_color=("#ffffff", "#2b2b2b"),
                text_color=("#2b2b2b", "#ffffff")
            )
        button.configure(
            fg_color=("#e0e0e0", "#3a3a3a"),
            text_color=("#000000", "#ffffff")
        )
        self.active_button = button
        
    def show_dashboard(self):
        self.hide_all()
        self.dashboard_frame.pack(fill="both", expand=True, padx=20, pady=20)
        if self.controller:
            self.controller.refresh_data()

    def show_room(self):
        self.hide_all()
        tab = self.lazy_load_tab("room", roomTab)
        if hasattr(tab, 'initialize'):
            tab.initialize()
        tab.pack(fill="both", expand=True, padx=20, pady=20)

    def show_tenant(self):
        self.hide_all()
        tab = self.lazy_load_tab("tenant", tenantTab)
        if hasattr(tab, 'initialize'):
            tab.initialize()
        tab.pack(fill="both", expand=True, padx=20, pady=20)

    def show_bill(self):
        self.hide_all()
        tab = self.lazy_load_tab("bill", billTab)
        if hasattr(tab, 'initialize'):
            tab.initialize()
        tab.pack(fill="both", expand=True, padx=20, pady=20)
        
    def show_report(self):
        self.hide_all()
        user_id = getattr(self.controller, 'current_user_id', None) if self.controller else None
        tab = self.lazy_load_tab("report", ReportTab, user_id=user_id)
        if hasattr(tab, 'initialize'):
            tab.initialize()
        tab.pack(fill="both", expand=True, padx=20, pady=20)

    def show_contract(self):
        self.hide_all()
        tab = self.lazy_load_tab("contract", contractTab)
        if hasattr(tab, 'initialize'):
            tab.initialize()
        tab.pack(fill="both", expand=True, padx=20, pady=20)


    def reload_room_card(self, occupied, total):
        self.room_card.update_value(f"{occupied}/{total}")

    def reload_tenant_card(self, count):
        self.tenant_card.update_value(str(count))

    def reload_payment_card(self, paid, total):
        self.payment_card.update_value(f"{paid}/{total}")

    def log_out(self):
        if not messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?", parent=self):
            return
        self.parent.show_login()