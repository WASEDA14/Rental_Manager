import customtkinter as ctk
from tkinter import messagebox
from views.room_tab import roomTab
from views.tenant_tab import tenantTab
from views.bill_tab import billTab
from views.contract_tab import contractView
from views.dashboard_tab import DashboardView
from views.login_tab import LoginTab  # Add this import
from controllers.dashboard_controller import DashboardController
from services.auth_service import AuthService  # Add this import

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rental Manager")
        self.geometry("1500x850")
        self.resizable(True, True)

        # Initialize services
        self.auth_service = AuthService()

        # Show login screen first
        self.show_login()

    def show_login(self):
        """Show the login screen"""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Create and show login tab
        self.login_tab = LoginTab(self, on_login_success=self.on_login_success)
        self.login_tab.pack(expand=True, fill="both")

        # Inject auth service
        self.login_tab.auth_service = self.auth_service

    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = {
            'login_id': user['login_id'],
            'user_name': user['user_name'],
            'email': user.get('email', '')
        }
        self.show_main_app()

    def show_main_app(self):
        """Show the main application after successful login"""
        # Clear login screen
        for widget in self.winfo_children():
            widget.destroy()

        self.setup_sidebar()
        self.setup_content()

        # Show dashboard by default
        self.show_dashboard()

    def setup_sidebar(self):
        """Set up the sidebar with user info and navigation"""
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # User info at the top
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        user_frame.pack(pady=(10, 20), padx=10, fill="x")

        ctk.CTkLabel(
            user_frame,
            text=self.current_user['user_name'],
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            user_frame,
            text=self.current_user['login_id'],
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()

        # Logout button
        logout_btn = ctk.CTkButton(
            user_frame,
            text="Logout",
            command=self.logout,
            fg_color="transparent",
            text_color=("gray50", "gray70"),
            hover_color=("gray70", "gray30"),
            font=("Arial", 12)
        )
        logout_btn.pack(pady=(10, 0))

        # Separator
        ctk.CTkFrame(self.sidebar, height=1, fg_color="gray70").pack(fill="x", padx=10, pady=10)

        # Menu buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.btn_room = ctk.CTkButton(self.sidebar, text="Rooms", command=self.show_room)
        self.btn_tenant = ctk.CTkButton(self.sidebar, text="Tenants", command=self.show_tenant)
        self.btn_bill = ctk.CTkButton(self.sidebar, text="Bills", command=self.show_bill)
        self.btn_contract = ctk.CTkButton(self.sidebar, text="Contracts", command=self.show_contract)

        for b in [self.btn_dashboard, self.btn_room, self.btn_tenant, self.btn_bill, self.btn_contract]:
            b.pack(fill="x", padx=10, pady=5)

    def setup_content(self):
        """Set up the main content area"""
        # Content area
        self.content = ctk.CTkFrame(self)
        self.content.pack(side="right", fill="both", expand=True)

        # Initialize controllers
        self.dashboard_controller = DashboardController()

        # Child pages (frames)
        self.dashboard_view = DashboardView(self.content, self.dashboard_controller)
        self.room_tab = roomTab(self.content)
        self.tenant_view = tenantTab(self.content)
        self.bill_view = billTab(self.content)
        self.contract_view = contractView(self.content)

        # Stack all pages on top of each other
        for frame in (
                self.dashboard_view,
                self.room_tab,
                self.tenant_view,
                self.bill_view,
                self.contract_view,
        ):
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    def logout(self):
        """Handle logout"""
        self.current_user = None
        self.show_login()

    # ===== View Switchers =====
    def show_dashboard(self):
        self.dashboard_controller.refresh_data()
        self.dashboard_view.tkraise()

    def show_room(self):
        self.room_tab.tkraise()

    def show_tenant(self):
        self.tenant_view.tkraise()

    def show_bill(self):
        self.bill_view.tkraise()

    def show_contract(self):
        self.contract_view.tkraise()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()