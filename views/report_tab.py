import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db import get_db
import pandas as pd

class ReportTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Báo cáo thống kê",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Create frames for each report
        self.occupancy_frame = ctk.CTkFrame(self.notebook, fg_color="transparent")
        self.payment_frame = ctk.CTkFrame(self.notebook, fg_color="transparent")
        self.tenant_frame = ctk.CTkFrame(self.notebook, fg_color="transparent")

        # Add frames to notebook
        self.notebook.add(self.occupancy_frame, text="Tình trạng phòng")
        self.notebook.add(self.payment_frame, text="Thanh toán")
        self.notebook.add(self.tenant_frame, text="Thống kê khách thuê")

        # Add refresh button
        refresh_btn = ctk.CTkButton(
            self.main_frame,
            text="Làm mới dữ liệu",
            command=self.load_data,
            width=150,
            height=40,
            corner_radius=8
        )
        refresh_btn.pack(side="right", pady=(10, 0))

    def load_data(self):
        self.plot_occupancy()
        self.plot_payments()
        self.plot_tenants()

    def plot_occupancy(self):
        # Clear previous plot
        for widget in self.occupancy_frame.winfo_children():
            widget.destroy()

        with get_db() as conn:
            df = pd.read_sql(
                """
                SELECT 
                    r.room_name,
                    CASE 
                        WHEN c.contract_id IS NOT NULL AND c.contract_status = 'active' 
                        THEN 'Đang thuê' 
                        ELSE 'Trống' 
                    END as status
                FROM room r
                LEFT JOIN contract c ON r.room_id = c.room_id 
                    AND c.contract_status = 'active'
                    AND c.is_deleted = 0
                WHERE r.is_deleted = 0
                """,
                conn
            )

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Plot data
        status_counts = df['status'].value_counts()
        status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        ax.set_title('Tỷ lệ phòng trống/đang thuê')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.occupancy_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def plot_payments(self):
        # Clear previous plot
        for widget in self.payment_frame.winfo_children():
            widget.destroy()

        with get_db() as conn:
            df = pd.read_sql(
                """
                SELECT 
                    bill_month as month,
                    SUM(total_amount) as total_amount,
                    SUM(CASE WHEN paid_status = 'paid' THEN total_amount ELSE 0 END) as paid_amount
                FROM bill
                WHERE is_deleted = 0
                GROUP BY bill_month
                ORDER BY month
                """,
                conn
            )

        if not df.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plot data
            df.plot(x='month', y=['total_amount', 'paid_amount'], kind='bar', ax=ax)
            ax.set_title('Doanh thu theo tháng')
            ax.set_xlabel('Tháng')
            ax.set_ylabel('Số tiền (VND)')
            ax.legend(['Tổng tiền', 'Đã thanh toán'])
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=self.payment_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def plot_tenants(self):
        # Clear previous plot
        for widget in self.tenant_frame.winfo_children():
            widget.destroy()

        with get_db() as conn:
            # Get tenant count over time based on contract start dates
            df = pd.read_sql(
                """
                SELECT 
                    strftime('%Y-%m', c.start_ymd) as month,
                    COUNT(DISTINCT t.tenant_id) as total_tenants
                FROM tenant t
                JOIN contract c ON t.tenant_id = c.tenant_id
                WHERE t.is_deleted = 0 AND c.is_deleted = 0
                GROUP BY strftime('%Y-%m', c.start_ymd)
                ORDER BY month
                """,
                conn
            )

        if not df.empty:
            # Calculate cumulative sum of tenants over time
            df['cumulative_tenants'] = df['total_tenants'].cumsum()
            
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # Plot data
            df.plot(x='month', y='cumulative_tenants', kind='line', marker='o', ax=ax)
            ax.set_title('Tổng số khách thuê theo thời gian')
            ax.set_xlabel('Tháng')
            ax.set_ylabel('Tổng số khách')
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, master=self.tenant_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
            # Add data labels
            for i, v in enumerate(df['cumulative_tenants']):
                ax.text(i, v, str(v), ha='center', va='bottom')
                
            plt.tight_layout()
