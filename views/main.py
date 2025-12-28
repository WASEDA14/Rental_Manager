import customtkinter as ctk
from tkinter import messagebox
from views.dashboard_tab import DashboardView
from views.login_tab import loginTab

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rental Manager")
        self.current_user = None

        # Bắt đầu với màn hình login
        self.show_login()

    def show_login(self):
        # Xóa hết nội dung cũ
        for widget in self.winfo_children():
            widget.destroy()

        # Reset về trạng thái login: kích thước nhỏ, không resize, giữa màn hình
        self.reset_to_login_state()

        # Tạo lại login tab
        self.login_tab = loginTab(master=self)
        self.login_tab.pack(fill='both', expand=True, padx=20, pady=20)

        # Đưa cửa sổ lên trên cùng và focus
        self.lift()
        self.focus_force()

    def reset_to_login_state(self):
        """Reset cửa sổ về trạng thái login: nhỏ, cố định, giữa màn hình"""
        self.geometry("480x680")
        self.resizable(False, False)
        self.state('normal')  # Thoát khỏi zoomed/fullscreen

        # Căn giữa màn hình
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 480) // 2
        y = (screen_height - 680) // 2
        self.geometry(f"480x680+{x}+{y}")

    def show_main_app(self):
        # Xóa login
        for widget in self.winfo_children():
            widget.destroy()

        # Chuyển sang giao diện chính: full màn hình
        self.title("Rental Manager - Hệ thống quản lý nhà trọ")
        self.resizable(True, True)
        self.state("zoomed")  # Toàn màn hình

        # Tạo dashboard
        self.dashboard = DashboardView(self)
        self.dashboard.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.show_main_app()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()