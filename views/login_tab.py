# views/login_tab.py
import customtkinter as ctk
from tkinter import messagebox
from typing import Callable


class LoginTab(ctk.CTkFrame):
    def __init__(self, parent, on_login_success: Callable, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.on_login_success = on_login_success
        self.auth_service = None  # Will be injected
        self.setup_ui()

    def setup_ui(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        container.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            container,
            text="Rental Manager Login",
            font=("Arial", 24, "bold")
        )
        title.grid(row=0, column=0, pady=(0, 30))

        # Login Form
        self.login_id_var = ctk.StringVar()
        self.login_password_var = ctk.StringVar()

        form_frame = ctk.CTkFrame(container, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="ew")

        # Login ID
        ctk.CTkLabel(
            form_frame,
            text="Login ID:",
            font=("Arial", 12)
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))

        login_id_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.login_id_var,
            width=300,
            height=40,
            font=("Arial", 14)
        )
        login_id_entry.grid(row=1, column=0, pady=(0, 15))
        login_id_entry.focus()  # Focus on login ID field by default

        # Password
        ctk.CTkLabel(
            form_frame,
            text="Password:",
            font=("Arial", 12)
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))

        password_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.login_password_var,
            show="•",
            width=300,
            height=40,
            font=("Arial", 14)
        )
        password_entry.grid(row=3, column=0, pady=(0, 20))

        # Bind Enter key to login
        password_entry.bind('<Return>', lambda e: self.handle_login())

        # Login Button
        login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.handle_login,
            height=40,
            font=("Arial", 14, "bold")
        )
        login_btn.grid(row=4, column=0, pady=(10, 0), sticky="ew")

    def handle_login(self):
        """Handle login button click"""
        login_id = self.login_id_var.get().strip()
        password = self.login_password_var.get()

        if not login_id or not password:
            messagebox.showerror("Error", "Please enter both login ID and password")
            return

        # Authenticate user
        user = self.auth_service.authenticate_user(login_id, password)

        if user:
            # Log successful login
            self.auth_service.log_login_attempt(login_id, True)
            # Clear password field
            self.login_password_var.set("")
            # Call the success callback with user data
            self.on_login_success(user)
        else:
            # Log failed login
            self.auth_service.log_login_attempt(login_id, False)
            messagebox.showerror("Login Failed", "Invalid login ID or password")
            self.login_password_var.set("")
            # Focus back to password field
            self.focus_set()