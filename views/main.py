import customtkinter as ctk
from views.dashboard_tab import DashboardView
from views.login_tab import loginTab

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Rental Manager")
        self.geometry("1500x850")
        self.resizable(True, True)
        self.show_login()

    def show_login(self):
        """Show the login screen"""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
            
        # Set window properties for login
        self.geometry("480x680")
        self.resizable(False, False)
        
        # Create and show login tab
        self.login_tab = loginTab(master=self)
        self.login_tab.pack(fill='both', expand=True, padx=20, pady=20)

    def show_main_app(self):
        # Clear login screen
        for widget in self.winfo_children():
            widget.destroy()
            
        # Set window properties for main app
        self.title("Rental Manager")
        self.geometry("1200x800")
        self.resizable(True, True)
        
        # Create and show dashboard
        self.dashboard = DashboardView(self)
        self.dashboard.pack(fill='both', expand=True)
        
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