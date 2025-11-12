import customtkinter as ctk
from GUI.room import RoomTab
from GUI.tentant import TenantTab
from GUI.bill import BillTab
from GUI.contract import ContractTab
from GUI.dashboard import DashboardTab

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rental Manager")
        self.geometry("1100x650")
        self.resizable(False, False)

        # ===== Sidebar =====
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)  # giữ width cố định
        ctk.CTkLabel(self.sidebar, text="Menu",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

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

        # Child pages (frames)
        self.dashboard_tab = DashboardTab(self.content)
        self.room_tab      = RoomTab(self.content)
        self.tenant_tab    = TenantTab(self.content)
        self.bill_tab      = BillTab(self.content)
        self.contract_tab  = ContractTab(self.content)

        # Chồng các page lên nhau
        for frame in (self.dashboard_tab, self.room_tab, self.tenant_tab, self.bill_tab, self.contract_tab):
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_dashboard()  # trang mặc định

    # ===== Switchers =====
    def show_dashboard(self): self.dashboard_tab.tkraise()
    def show_room(self):      self.room_tab.tkraise()
    def show_tenant(self):    self.tenant_tab.tkraise()
    def show_bill(self):      self.bill_tab.tkraise()
    def show_contract(self):  self.contract_tab.tkraise()

if __name__ == "__main__":
    MainWindow().mainloop()