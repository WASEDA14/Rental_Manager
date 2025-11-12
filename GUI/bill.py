# GUI/bill.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.bill_service import BillService

class BillTab(ctk.CTkFrame):
    def __init__(self, parent, bill_service: BillService = None):
        super().__init__(parent)
        self.svc = bill_service or BillService()
        self._selected_id = None

        # ===== Form =====
        form = ctk.CTkFrame(self); form.pack(fill="x", padx=12, pady=(10,5))

        self.name_var = ctk.StringVar()
        self.room_var = ctk.StringVar()
        self.month_var = ctk.StringVar()
        self.total_var = ctk.StringVar()
        self.search_var = ctk.StringVar()

        ctk.CTkLabel(form, text="Tenant").grid(row=0, column=0, padx=6, pady=6)
        ctk.CTkEntry(form, textvariable=self.name_var, width=150).grid(row=0, column=1, padx=6, pady=6)
        ctk.CTkLabel(form, text="Room ID").grid(row=0, column=2, padx=6, pady=6)
        ctk.CTkEntry(form, textvariable=self.room_var, width=100).grid(row=0, column=3, padx=6, pady=6)
        ctk.CTkLabel(form, text="Month").grid(row=0, column=4, padx=6, pady=6)
        ctk.CTkEntry(form, textvariable=self.month_var, width=100, placeholder_text="YYYY-MM").grid(row=0, column=5, padx=6, pady=6)
        ctk.CTkLabel(form, text="Total Amount (VNĐ)").grid(row=0, column=6, padx=6, pady=6)
        ctk.CTkEntry(form, textvariable=self.total_var, width=100).grid(row=0, column=7, padx=6, pady=6)
        ctk.CTkButton(form, text="Add", fg_color="#27ae60", command=self.on_add).grid(row=0, column=8, padx=8)
        ctk.CTkButton(form, text="Edit", fg_color="#f39c12", command=self.on_update).grid(row=0, column=9, padx=4)

        # Tìm kiếm
        ctk.CTkLabel(form, text="Search").grid(row=1, column=0, padx=6, pady=(0,6))
        ctk.CTkEntry(form, textvariable=self.search_var, width=160).grid(row=1, column=1, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Filter", command=self.reload).grid(row=1, column=2, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Refresh", command=self.on_clear).grid(row=1, column=3, padx=6, pady=(0,6))

        # ===== Bảng =====
        table = ctk.CTkFrame(self); table.pack(fill="both", expand=True, padx=12, pady=5)
        cols = ("id","tenant","room","month","total","status","created")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=14)
        for c, t, w in [
            ("id","ID",60),("tenant","Khách",150),("room","Phòng",80),
            ("month","Tháng",80),("total","Tổng (VNĐ)",100),
            ("status","Tình trạng",90),("created","Tạo lúc",130)]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set); sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

        # ===== Dưới cùng =====
        bottom = ctk.CTkFrame(self, fg_color="transparent"); bottom.pack(fill="x", padx=12, pady=6)
        # ctk.CTkButton(bottom, text="Đánh dấu đã thanh toán", command=self.on_paid).pack(side="left")
        ctk.CTkButton(bottom, text="Xóa", fg_color="#e74c3c", command=self.on_delete).pack(side="right")

        self.reload()

    def reload(self):
        kw = self.search_var.get().strip() or None
        rows = self.svc.list(kw)
        self.tree.delete(*self.tree.get_children())
        for b in rows:
            self.tree.insert("", "end", values=(
                b.id, b.tenant_name, b.room_code, b.month,
                f"{b.total:,.0f}", "Đã trả" if b.paid else "Chưa",
                b.created_at
            ))

    def on_clear(self):
        for v in (self.name_var, self.room_var, self.month_var, self.total_var, self.search_var):
            v.set("")
        self._selected_id = None
        self.reload()

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self._selected_id = int(v[0])
        self.name_var.set(v[1])
        self.room_var.set(v[2])
        self.month_var.set(v[3])
        self.total_var.set(v[4].replace(",",""))

    def on_add(self):
        try:
            self.svc.create(
                tenant_name=self.name_var.get(),
                room_code=self.room_var.get(),
                month=self.month_var.get(),
                total=float(self.total_var.get() or 0),
            )
            self.on_clear()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_update(self):
        if not self._selected_id: return
        try:
            self.svc.update(
                self._selected_id,
                total=float(self.total_var.get() or 0)
            )
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_paid(self):
        if not self._selected_id: return
        try:
            self.svc.mark_paid(self._selected_id)
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete(self):
        if not self._selected_id: return
        if messagebox.askyesno("Xóa", "Xóa hóa đơn này?"):
            self.svc.delete(self._selected_id)
            self.on_clear()
