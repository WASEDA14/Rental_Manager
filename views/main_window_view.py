import customtkinter as ctk

from views.room_tab import roomTab
from views.tenant_tab import tenantTab
from views.bill_tab import billTab
from views.contract_tab import contractView
from views.dashboard_tab import DashboardView
from controllers.dashboard_controller import DashboardController

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rental Manager")
        self.geometry("1500x850")
        self.resizable(True, True)

        # ===== Sidebar =====
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # giữ width cố định
        ctk.CTkLabel(
            self.sidebar,
            text="Menu",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)

        # Menu buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.btn_room      = ctk.CTkButton(self.sidebar, text="Rooms",     command=self.show_room)
        self.btn_tenant    = ctk.CTkButton(self.sidebar, text="Tenants",   command=self.show_tenant)
        self.btn_bill      = ctk.CTkButton(self.sidebar, text="Bills",     command=self.show_bill)
        self.btn_contract  = ctk.CTkButton(self.sidebar, text="Contracts", command=self.show_contract)

        for b in [self.btn_dashboard, self.btn_room, self.btn_tenant, self.btn_bill, self.btn_contract]:
            b.pack(fill="x", padx=10, pady=5)

        # ===== Content area =====
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)

        # Initialize controllers
        self.dashboard_controller = DashboardController(None)  # View will be set in DashboardView.__init__
        
        # Child pages (frames)
        self.dashboard_view = DashboardView(self.content, self.dashboard_controller)
        self.room_tab = roomTab(self.content)
        self.tenant_view = tenantTab(self.content)
        self.bill_view = billTab(self.content)
        self.contract_view = contractView(self.content)

        # Chồng các page lên nhau
        for frame in (
            self.dashboard_view,
            self.room_tab,
            self.tenant_view,
            self.bill_view,
            self.contract_view,
        ):
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_dashboard()

    # ===== Switchers =====
    def show_dashboard(self): self.dashboard_view.tkraise()
    def show_room(self):      self.room_tab.tkraise()
    def show_tenant(self):    self.tenant_view.tkraise()
    def show_bill(self):      self.bill_view.tkraise()
    def show_contract(self):  self.contract_view.tkraise()


if __name__ == "__main__":
    MainWindow().mainloop()
