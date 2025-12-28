# ui/tabs/report_tab.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from module.report_service import (
    get_room_report,
    get_tenant_report,
    get_contract_report,
    get_bill_report,
)


class ReportTab(ctk.CTkFrame):
    def __init__(self, master, user_id=None):
        super().__init__(master, fg_color="#f8fafc")
        self.user_id = user_id
        self.chart_frames = []

        self._create_ui()
        self.refresh_data()

    def initialize(self):
        self.refresh_data()

    def refresh_data(self):
        for frame in self.chart_frames:
            frame.destroy()
        self.chart_frames.clear()
        self._create_charts()

    def _create_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(30, 40), padx=50)

        ctk.CTkLabel(
            header,
            text="BÁO CÁO & THỐNG KÊ",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#1e293b"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Tổng quan hoạt động hệ thống",
            font=ctk.CTkFont(size=16),
            text_color="#64748b"
        ).pack(anchor="w", pady=(10, 0))

        # Grid 2x2 cho 4 biểu đồ lớn
        self.charts_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_grid.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        self.charts_grid.grid_rowconfigure((0, 1), weight=1)
        self.charts_grid.grid_columnconfigure((0, 1), weight=1)

    def _create_charts(self):
        room = get_room_report()
        tenant = get_tenant_report()
        contract = get_contract_report()
        bill = get_bill_report()

        self._create_bar_room(self.charts_grid, 0, 0, room)          # ĐÃ ĐỔI THÀNH BAR
        self._create_bar_bill(self.charts_grid, 0, 1, bill)
        self._create_pie_tenant(self.charts_grid, 1, 0, tenant)
        self._create_bar_contract(self.charts_grid, 1, 1, contract)

    def _create_chart_container(self, parent, row, col, title):
        container = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=20,
            border_width=1,
            border_color="#e2e8f0"
        )
        container.grid(row=row, column=col, padx=25, pady=25, sticky="nsew")

        title_label = ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#1e293b"
        )
        title_label.pack(pady=(30, 20))

        chart_area = ctk.CTkFrame(container, fg_color="white")
        chart_area.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.chart_frames.append(container)
        return chart_area

    def _embed_chart(self, fig, frame):
        fig.tight_layout(pad=4.0)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _no_data_chart(self, ax, message="Chưa có dữ liệu"):
        ax.text(0.5, 0.5, message, transform=ax.transAxes,
                fontsize=18, color="#94a3b8", ha="center", va="center", weight="bold")
        ax.axis('off')

    # === 1. Tình trạng phòng trọ - BAR CHART (cột dọc) ===
    def _create_bar_room(self, parent, row, col, data):
        frame = self._create_chart_container(parent, row, col, "Tình trạng phòng trọ")
        fig = Figure(figsize=(8, 6), dpi=100)  # PHÓNG TO
        ax = fig.add_subplot(111)

        labels = ["Đang thuê", "Trống", "Bảo trì"]
        values = [data["occupied"], data["available"], data["maintenance"]]
        colors = ["#3b82f6", "#10b981", "#f59e0b"]

        total = sum(values)
        if total == 0:
            self._no_data_chart(ax)
        else:
            bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor="white", linewidth=3)

            ax.set_ylim(0, max(values) * 1.4 if max(values) > 0 else 10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e2e8f0')
            ax.spines['bottom'].set_color('#e2e8f0')
            ax.grid(axis='y', linestyle='--', alpha=0.4, color='#e2e8f0')

            for bar in bars:
                height = int(bar.get_height())
                if height > 0:
                    ax.text(
                        bar.get_x() + bar.get_width()/2,
                        height + max(values)*0.02,
                        str(height),
                        ha='center',
                        va='bottom',
                        fontweight='bold',
                        fontsize=20,
                        color='#1e293b'
                    )

            ax.tick_params(axis='x', labelsize=14)
            ax.tick_params(axis='y', labelsize=12)

        self._embed_chart(fig, frame)

    # === 2. Hóa đơn - Bar ngang (giữ nguyên nhưng phóng to) ===
    def _create_bar_bill(self, parent, row, col, data):
        frame = self._create_chart_container(parent, row, col, "Tình trạng hóa đơn")
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        paid = data["paid"]
        unpaid = data["unpaid"]
        total = paid + unpaid

        if total == 0:
            self._no_data_chart(ax)
        else:
            categories = ["Đã thanh toán", "Chưa thanh toán"]
            values = [paid, unpaid]
            colors = ["#16a34a", "#ef4444"]

            bars = ax.barh(categories, values, color=colors, height=0.6, edgecolor="white", linewidth=3)

            ax.set_xlim(0, max(values) * 1.4 if max(values) > 0 else 10)
            ax.invert_yaxis()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e2e8f0')
            ax.spines['bottom'].set_color('#e2e8f0')

            for bar in bars:
                width = int(bar.get_width())
                if width > 0:
                    ax.text(
                        width + max(values)*0.02,
                        bar.get_y() + bar.get_height()/2,
                        str(width),
                        va='center',
                        fontweight='bold',
                        fontsize=20,
                        color='#1e293b'
                    )

            ax.tick_params(axis='y', labelsize=14)
            ax.tick_params(axis='x', labelsize=12)

        self._embed_chart(fig, frame)

    # === 3. Khách thuê - Pie Chart (phóng to) ===
    def _create_pie_tenant(self, parent, row, col, data):
        frame = self._create_chart_container(parent, row, col, "Khách thuê")
        fig = Figure(figsize=(8, 7), dpi=100)
        ax = fig.add_subplot(111)

        active = data["active"]
        new = data["new_this_month"]
        total = active + new

        if total == 0:
            self._no_data_chart(ax)
        else:
            values = [active, new]
            labels = ["Đang ở", "Mới tháng này"]
            colors = ["#10b981", "#8b5cf6"]

            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                colors=colors,
                autopct=lambda pct: f"{int(pct/100.*total)}" if pct > 8 else "",
                startangle=90,
                wedgeprops=dict(edgecolor='white', linewidth=4),
                textprops=dict(color="white", weight="bold", fontsize=16)
            )

        ax.axis('equal')
        self._embed_chart(fig, frame)

    # === 4. Hợp đồng - Bar dọc (phóng to) ===
    def _create_bar_contract(self, parent, row, col, data):
        frame = self._create_chart_container(parent, row, col, "Tình trạng hợp đồng")
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)

        new = data["new_this_month"]
        soon = data["soon_expire"]
        ended = data["ended"]
        total = new + soon + ended

        if total == 0:
            self._no_data_chart(ax)
        else:
            labels = ["Mới tháng này", "Sắp hết hạn", "Đã kết thúc"]
            values = [new, soon, ended]
            colors = ["#8b5cf6", "#f59e0b", "#94a3b8"]

            bars = ax.bar(labels, values, color=colors, width=0.6, edgecolor="white", linewidth=3)

            ax.set_ylim(0, max(values) * 1.4 if max(values) > 0 else 10)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#e2e8f0')
            ax.spines['bottom'].set_color('#e2e8f0')
            ax.grid(axis='y', linestyle='--', alpha=0.4, color='#e2e8f0')

            for bar in bars:
                height = int(bar.get_height())
                if height > 0:
                    ax.text(
                        bar.get_x() + bar.get_width()/2,
                        height + max(values)*0.02,
                        str(height),
                        ha='center',
                        va='bottom',
                        fontweight='bold',
                        fontsize=20,
                        color='#1e293b'
                    )

            ax.tick_params(axis='x', labelsize=13, rotation=15)
            ax.tick_params(axis='y', labelsize=12)

        self._embed_chart(fig, frame)