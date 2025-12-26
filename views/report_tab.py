# ui/tabs/report_tab.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from services.report_service import (
    get_room_report,
    get_tenant_report,
    get_contract_report,
    get_bill_report,
)


class ReportTab(ctk.CTkFrame):
    def __init__(self, master, user_id):
        super().__init__(master, fg_color="transparent")
        self._create_header()
        self._create_charts()

    def _create_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 15), padx=40)

        ctk.CTkLabel(
            header,
            text="BÁO CÁO TỔNG QUAN",
            font=("Inter", 32, "bold"),
            text_color="#1e293b",
        ).pack()

        ctk.CTkLabel(
            header,
            text="Dữ liệu báo cáo thống kê",
            font=("Inter", 14),
            text_color="#64748b",
        ).pack(pady=(0, 20))

    def _create_charts(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=35, pady=10)
        main.grid_rowconfigure((0, 1), weight=1)
        main.grid_columnconfigure((0, 1), weight=1)

        room = get_room_report()
        tenant = get_tenant_report()
        contract = get_contract_report()
        bill = get_bill_report()

        self._bar_room(main, 0, 0, room)
        self._bar_bill(main, 0, 1, bill)
        self._pie_tenant(main, 1, 0, tenant)
        self._vbar_contract(main, 1, 1, contract)

    # === BIỂU ĐỒ PHÒNG ===
    def _bar_room(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        values = [data["occupied"], data["available"], data["maintenance"]]
        total = sum(values)

        if total == 0:
            self._no_data(ax, "Chưa có dữ liệu phòng")
        else:
            labels = ["Đang thuê", "Trống", "Bảo trì"]
            colors = ["#0067F7", "#00B63E", "#f59e0b"]
            bars = ax.bar(
                labels,
                values,
                color=colors,
                width=0.6,
                edgecolor="black",
                linewidth=1.2,
            )

            ax.set_title(
                "PHÒNG TRỌ", fontsize=13, fontweight="bold", pad=12, color="#1e293b"
            )
            ax.set_ylabel("Số lượng", fontsize=10)
            max_y = 10
            ax.set_yticks(range(0, max_y + 1))
            ax.set_ylim(0, max_y)
            for bar in bars:
                h = int(bar.get_height())
                if h > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        h + max(values) * 0.02,
                        str(h),
                        ha="center",
                        va="bottom",
                        fontweight="bold",
                        fontsize=15,
                        color="#1e293b",
                    )

        self._embed(fig, frame)

    # === BIỂU ĐỒ HÓA ĐƠN ===
    def _bar_bill(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        values = [data["paid"], data["unpaid"]]
        total = sum(values)

        if total == 0:
            self._no_data(ax, "Chưa có hóa đơn")
        else:
            labels = ["Đã thanh toán", "Chưa thanh toán"]
            colors = ["#16a34a", "#F50002"]
            bars = ax.bar(
                labels,
                values,
                color=colors,
                width=0.55,
                edgecolor="black",
                linewidth=1.2,
            )

            ax.set_title(
                "HÓA ĐƠN", fontsize=13, fontweight="bold", pad=12, color="#1e293b"
            )
            ax.set_ylabel("Số lượng", fontsize=10)
            max_y = 10
            ax.set_yticks(range(0, max_y + 1))  # Show whole numbers from 0 to 10
            ax.set_ylim(0, max_y)  # Set Y-axis limit

            for bar in bars:
                h = int(bar.get_height())
                if h > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        h + max(values) * 0.02,
                        str(h),
                        ha="center",
                        va="bottom",
                        fontweight="bold",
                        fontsize=15,
                        color="#1e293b",
                    )

        self._embed(fig, frame)

    # === BIỂU ĐỒ TRÒN KHÁCH THUÊ ===
    def _pie_tenant(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        values = [data["active"], data["new_this_month"]]
        total = sum(values)

        if total == 0:
            self._no_data(ax, "Chưa có khách thuê")
        else:
            labels = ["Đang thuê", "Mới tháng này"]
            colors = ["#00B63E", "#8b5cf6"]

            # Hàm autopct: tránh chia cho 0
            def make_autopct(vals):
                def my_autopct(pct):
                    total_sum = sum(vals)
                    if total_sum == 0:
                        return ""
                    val = int(round(pct * total_sum / 100.0))
                    return f"{val}" if val > 0 else ""

                return my_autopct

            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,
                autopct=make_autopct(values),
                colors=colors,
                startangle=90,
                wedgeprops={"edgecolor": "white", "linewidth": 2},
                textprops={"fontsize": 11, "weight": "bold", "color": "white"},
            )

            ax.set_title("KHÁCH THUÊ", fontsize=13, fontweight="bold", pad=12)

            # Legend
            ax.legend(
                wedges,
                [f"{l}: {v}" for l, v in zip(labels, values) if v > 0],
                loc="lower center",
                bbox_to_anchor=(0.5, -0.1),
                ncol=2,
                fontsize=10,
            )

        self._embed(fig, frame)

    # === BIỂU ĐỒ HỢP ĐỒNG ===
    def _vbar_contract(self, parent, r, c, data):
        frame = self._chart_frame(parent, r, c)
        fig = Figure(figsize=(4.3, 3.5), dpi=100)
        ax = fig.add_subplot(111)

        values = [data["new_this_month"], data["soon_expire"], data["ended"]]
        total = sum(values)

        if total == 0:
            self._no_data(ax, "Chưa có hợp đồng")
        else:
            labels = ["Mới", "Sắp hết", "Đã hết"]
            colors = ["#8b5cf6", "#f59e0b", "#94a3b8"]

            x = np.arange(len(labels))
            bars = ax.bar(
                x, values, color=colors, width=0.55, edgecolor="black", linewidth=1.2
            )

            ax.set_xticks(x)
            ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
            ax.set_title("HỢP ĐỒNG", fontsize=13, fontweight="bold", pad=12)
            ax.grid(True, axis="y", linestyle="--", alpha=0.4)
            ax.set_ylim(0, max(values) * 1.3 or 1)

            for bar in bars:
                h = int(bar.get_height())
                if h > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        h + max(values) * 0.02,
                        str(h),
                        ha="center",
                        va="bottom",
                        fontweight="bold",
                        fontsize=15,
                    )

        self._embed(fig, frame)

    def _chart_frame(self, parent, r, c):
        f = ctk.CTkFrame(
            parent,
            fg_color="white",
            corner_radius=16,
            border_width=2,
            border_color="#e2e8f0",
        )
        f.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")
        return f

    def _embed(self, fig, frame):
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=12)
        canvas.draw()

    def _no_data(self, ax, message="Chưa có dữ liệu"):
        ax.text(
            0.5,
            0.5,
            message,
            ha="center",
            va="center",
            fontsize=16,
            color="#94a3b8",
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(False)
