# ui/login.py
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from services.login_service import authenticate_user
from views.dashboard_tab import DashboardView


# =====================================#
# =====================================#
# =====================================#
class loginTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        
        # Configure the main window through the master
        self.master.title("Đăng nhập hệ thống - Hệ thống quản lý nhà trọ")
        self.master.geometry("480x680")
        self.master.resizable(False, False)
        
        # Center the window
        self._center_window()
        
        # Configure the frame to expand
        self.pack(fill='both', expand=True, padx=20, pady=20)

        self._build_ui()

    def _center_window(self):
        self.master.update_idletasks()
        width = 480
        height = 680
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        self.configure(fg_color="#E8F0FE")

        container = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=10,
            border_width=1,
            border_color="#ffffff",
        )
        container.pack(fill="both", expand=True, padx=40, pady=40)

        # try:
        #     logo_img = Image.open(LOGO_PNG)
        #     logo = ctk.CTkImage(
        #         light_image=logo_img, dark_image=logo_img, size=(200, 40)
        #     )
        #     ctk.CTkLabel(container, image=logo, text="").pack(pady=(50, 10))
        # except:
        #     ctk.CTkLabel(container, text="LOGO", font=("Inter", 50)).pack(pady=(50, 10))

        ctk.CTkLabel(
            container,
            text="Đăng nhập hệ thống",
            font=("Inter", 22, "bold"),
            text_color="#131313",
        ).pack(pady=(20, 0))
        ctk.CTkLabel(
            container,
            text="Nhập tên tài khoản và mật khẩu quản trị hệ thống",
            font=("Inter", 13),
            text_color="#888888",
        ).pack(pady=(0, 30))

        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(padx=50, fill="x")

        ctk.CTkLabel(form, text="Tên tài khoản", font=("Inter", 14, "bold")).pack(
            anchor="w", pady=(0, 5)
        )
        self.entry_loginId = ctk.CTkEntry(
            form,
            placeholder_text="Nhập tên tài khoản",
            height=50,
            corner_radius=10,
            font=("Inter", 16),
            fg_color="#f8fafc",
        )
        self.entry_loginId.pack(fill="x", pady=(0, 20))
        self.entry_loginId.focus()

        ctk.CTkLabel(form, text="Mật khẩu", font=("Inter", 14, "bold")).pack(
            anchor="w", pady=(0, 5)
        )
        self.entry_pass = ctk.CTkEntry(
            form,
            placeholder_text="Nhập mật khẩu",
            show="*",
            height=50,
            corner_radius=10,
            font=("Inter", 16),
            fg_color="#f8fafc",
        )
        self.entry_pass.pack(fill="x", pady=(0, 40))

        ctk.CTkButton(
            form,
            text="Đăng nhập ngay",
            command=self.login,
            height=50,
            corner_radius=10,
            font=("Inter", 16, "bold"),
            fg_color="#0042DC",
            hover_color="#013BC4",
        ).pack(fill="x")

        ctk.CTkLabel(
            container,
            text="Hệ thống quản lý nhà trọ © 2025 Nhóm 8",
            font=("Inter", 12),
            text_color="#000",
        ).pack(side="bottom", pady=30)

        self.entry_loginId.bind("<Return>", lambda e: self.entry_pass.focus())
        self.entry_pass.bind("<Return>", lambda e: self.login())

    def login(self):
        user = self.entry_loginId.get().strip()
        pwd = self.entry_pass.get().strip()

        if not user or not pwd:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ!", parent=self)
            return

        result = authenticate_user(user, pwd)
        if result:
            # Since authenticate_user returns a SQLite row object, we can access columns by index
            # The query only selects 'user_name', so that's all we can access
            user_data = {
                'login_id': user,  # We already have this from the input
                'user_name': result[0] if result else None  # First (and only) column is user_name
            }

            if hasattr(self.master, 'on_login_success'):
                self.master.on_login_success(user_data)
            else:
                # Fallback if on_login_success is not available
                self.master.show_main_app()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu!", parent=self)
            self.entry_pass.delete(0, "end")
            self.entry_loginId.focus()
