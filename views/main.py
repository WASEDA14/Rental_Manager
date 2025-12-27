import customtkinter as ctk
from views.dashboard_tab import DashboardView
from views.login_tab import loginTab

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rental Manager")
        self.geometry("1600x850")
        self.resizable(True, True)
        self.show_login()

    def show_login(self):
        # Clear all widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Reset window properties
        # self.title("Đăng nhập hệ thống - Hệ thống quản lý nhà trọ")
        # self.state('normal')  # Remove maximized/zoomed state
        # self.geometry("480x680")
        # self.resizable(False, False)

        # Force update to apply changes
        self.update_idletasks()

        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 480) // 2
        y = (screen_height - 680) // 2
        self.geometry(f"480x680+{x}+{y}")

        # Recreate login tab
        self.login_tab = loginTab(master=self)
        self.login_tab.pack(fill='both', expand=True, padx=20, pady=20)

    def show_main_app(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.title("Rental Manager")

        # THÁO KHÓA LOGIN
        self.resizable(True, True)
        self.state("zoomed")  # FULL MÀN HÌNH

        # DASHBOARD
        self.dashboard = DashboardView(self)
        self.dashboard.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = {
            'login_id': user['login_id'],
            'user_name': user['user_name'],
            'email': user.get('email', '')
        }
        self.show_main_app()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()