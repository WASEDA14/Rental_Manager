# views/bill_view.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from models.bill_model import BillModel


class billView(ctk.CTkFrame):
    def __init__(self, parent, bill_service: BillModel | None = None):
        super().__init__(parent)
        self.svc = bill_service or BillModel()
        self._selected_id: int | None = None

        # ====== FORM TRÊN CÙNG – INFO CHUNG ======
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=(10, 4))

        self.tenantName_var = ctk.StringVar()
        self.roomName_var   = ctk.StringVar()
        self.month_var      = ctk.StringVar()
        self.total_var      = ctk.StringVar()
        self.note_var       = ctk.StringVar()
        self.search_var     = ctk.StringVar()

        # Paid info
        self.status_var      = ctk.StringVar(value="Unpaid")   # Unpaid / Partial / Paid
        self.paid_amount_var = ctk.StringVar()
        self.paid_date_var   = ctk.StringVar()

        # -------- hàng 0: tên KH, phòng, tháng, total --------
        ctk.CTkLabel(form, text="Customer Name").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.tenantName_var, width=160) \
            .grid(row=0, column=1, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(form, text="Room Name").grid(row=0, column=2, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.roomName_var, width=120) \
            .grid(row=0, column=3, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(form, text="Month").grid(row=0, column=4, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.month_var, width=80, placeholder_text="YYYY-MM") \
            .grid(row=0, column=5, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(form, text="Total (VND)").grid(row=0, column=6, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.total_var, width=120) \
            .grid(row=0, column=7, padx=6, pady=4, sticky="w")

        # -------- hàng 1: Note + status + paid date / amount --------
        ctk.CTkLabel(form, text="Note").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.note_var, width=300) \
            .grid(row=1, column=1, padx=6, pady=4, sticky="we", columnspan=3)

        # status combobox
        ctk.CTkLabel(form, text="Status").grid(row=1, column=4, padx=6, pady=4, sticky="e")
        self.status_cb = ttk.Combobox(
            form,
            textvariable=self.status_var,
            values=["Unpaid", "Partial", "Paid"],
            width=10,
            state="readonly",
        )
        self.status_cb.grid(row=1, column=5, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(form, text="Paid Amount").grid(row=1, column=6, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.paid_amount_var, width=100) \
            .grid(row=1, column=7, padx=6, pady=4, sticky="w")

        ctk.CTkLabel(form, text="Paid date").grid(row=1, column=8, padx=6, pady=4, sticky="w")
        paid_date = DateEntry(
            form,
            textvariable=self.paid_date_var,
            width=10,
            date_pattern="yyyy-mm-dd",
            foreground="black",
            background="white",
            selectbackground="blue",
            selectforeground="white",
        )
        paid_date.grid(row=1, column=9, padx=6, pady=4, sticky="w")

        # ====== KHỐI CHI TIẾT: ĐIỆN / NƯỚC / RENT / OTHER ======
        detail = ctk.CTkFrame(self)
        detail.pack(fill="x", padx=12, pady=(0, 6))

        # vars
        self.elec_prev_var   = ctk.StringVar()
        self.elec_curr_var   = ctk.StringVar()
        self.elec_price_var  = ctk.StringVar()
        self.water_prev_var  = ctk.StringVar()
        self.water_curr_var  = ctk.StringVar()
        self.water_price_var = ctk.StringVar()
        self.room_rent_var   = ctk.StringVar()
        self.other_fee_var   = ctk.StringVar()
        self.elec_amount_var  = ctk.StringVar()
        self.water_amount_var = ctk.StringVar()

        # Điện
        ctk.CTkLabel(detail, text="Electric prev").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.elec_prev_var, width=80) \
            .grid(row=0, column=1, padx=4, pady=4)
        ctk.CTkLabel(detail, text="current").grid(row=0, column=2, padx=4, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.elec_curr_var, width=80) \
            .grid(row=0, column=3, padx=4, pady=4)
        ctk.CTkLabel(detail, text="unit").grid(row=0, column=4, padx=4, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.elec_price_var, width=80) \
            .grid(row=0, column=5, padx=4, pady=4)
        ctk.CTkLabel(detail, text="Elec amount").grid(row=0, column=6, padx=4, pady=4, sticky="e")
        ctk.CTkEntry(detail, textvariable=self.elec_amount_var, width=100, state="disabled") \
            .grid(row=0, column=7, padx=4, pady=4)

        # Nước
        ctk.CTkLabel(detail, text="Water prev").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.water_prev_var, width=80) \
            .grid(row=1, column=1, padx=4, pady=4)
        ctk.CTkLabel(detail, text="current").grid(row=1, column=2, padx=4, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.water_curr_var, width=80) \
            .grid(row=1, column=3, padx=4, pady=4)
        ctk.CTkLabel(detail, text="unit").grid(row=1, column=4, padx=4, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.water_price_var, width=80) \
            .grid(row=1, column=5, padx=4, pady=4)
        ctk.CTkLabel(detail, text="Water amount").grid(row=1, column=6, padx=4, pady=4, sticky="e")
        ctk.CTkEntry(detail, textvariable=self.water_amount_var, width=100, state="disabled") \
            .grid(row=1, column=7, padx=4, pady=4)

        # Rent + Other + Total
        ctk.CTkLabel(detail, text="Room rent").grid(row=2, column=0, padx=6, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.room_rent_var, width=100) \
            .grid(row=2, column=1, padx=4, pady=4, sticky="w")

        ctk.CTkLabel(detail, text="Other fee").grid(row=2, column=2, padx=4, pady=4, sticky="w")
        ctk.CTkEntry(detail, textvariable=self.other_fee_var, width=100) \
            .grid(row=2, column=3, padx=4, pady=4, sticky="w")

        ctk.CTkButton(detail, text="Recalc total", command=self.on_recalc) \
            .grid(row=2, column=4, padx=8, pady=4)

        # ====== HÀNG TÌM KIẾM + NÚT CRUD ======
        ctk.CTkLabel(form, text="Search").grid(row=3, column=0, padx=6, pady=(4, 6), sticky="w")
        ctk.CTkEntry(form, textvariable=self.search_var, width=160) \
            .grid(row=3, column=1, padx=6, pady=(4, 6), sticky="w")

        ctk.CTkButton(form, text="Search", command=self.reload) \
            .grid(row=3, column=2, padx=6, pady=(4, 6))
        ctk.CTkButton(form, text="Clear", command=self.on_clear) \
            .grid(row=3, column=3, padx=6, pady=(4, 6))
        ctk.CTkButton(form, text="Add", fg_color="#27ae60", command=self.on_add) \
            .grid(row=3, column=4, padx=6, pady=(4, 6))
        ctk.CTkButton(form, text="Update", fg_color="#f39c12", command=self.on_update) \
            .grid(row=3, column=5, padx=6, pady=(4, 6))
        ctk.CTkButton(form, text="Export PDF", fg_color="#3498db", command=self.on_export) \
            .grid(row=3, column=6, padx=6, pady=(4, 6))

        for i in range(10):
            form.grid_columnconfigure(i, weight=0)
        form.grid_columnconfigure(1, weight=1)

        # ====== BẢNG LIST BILL ======
        table = ctk.CTkFrame(self)
        table.pack(fill="both", expand=True, padx=12, pady=4)

        cols = ("id", "tenant", "room", "month", "total", "status", "paid_ymd", "note")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=14)

        headings = {
            "id": "ID",
            "tenant": "Customer Name",
            "room": "Room Name",
            "month": "Month",
            "total": "Total (VND)",
            "status": "Status",
            "paid_ymd": "Paid Date",
            "note": "Note",
        }
        widths = {
            "id": 50,
            "tenant": 140,
            "room": 80,
            "month": 80,
            "total": 110,
            "status": 80,
            "paid_ymd": 100,
            "note": 150,
        }
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(
                c,
                width=widths[c],
                anchor=("center" if c in ("id", "room", "month", "status") else "w"),
            )
        self.tree.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

        # ====== NÚT DƯỚI CÙNG ======
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkButton(bottom, text="Delete", fg_color="#e74c3c", command=self.on_delete) \
            .pack(side="right")

        self.reload()

    # ================= Helpers =================
    @staticmethod
    def _to_int(s: str | None) -> int:
        s = (s or "").strip()
        return int(s) if s else 0

    def _status_to_int(self) -> int:
        val = self.status_var.get()
        if val == "Unpaid":
            return 0
        if val == "Partial":
            return 1
        return 2  # Paid

    def _status_from_int(self, v: int) -> str:
        return {0: "Unpaid", 1: "Partial", 2: "Paid"}.get(v, "Unpaid")

    # ================= CALC =================
    def on_recalc(self):
        try:
            elec_prev  = self._to_int(self.elec_prev_var.get())
            elec_curr  = self._to_int(self.elec_curr_var.get())
            elec_price = self._to_int(self.elec_price_var.get())
            water_prev  = self._to_int(self.water_prev_var.get())
            water_curr  = self._to_int(self.water_curr_var.get())
            water_price = self._to_int(self.water_price_var.get())
            room_rent   = self._to_int(self.room_rent_var.get())
            other       = self._to_int(self.other_fee_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Các trường số phải là số nguyên.")
            return

        elec_amount  = max(elec_curr - elec_prev, 0) * elec_price
        water_amount = max(water_curr - water_prev, 0) * water_price
        total = elec_amount + water_amount + room_rent + other

        self.elec_amount_var.set(str(elec_amount))
        self.water_amount_var.set(str(water_amount))
        self.total_var.set(str(total))

    # ================= CRUD =================
    def reload(self):
        kw = self.search_var.get().strip() or None
        rows = self.svc.list(kw)
        self.tree.delete(*self.tree.get_children())
        for b in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    b.id,
                    b.tenant_name,
                    b.room_code,
                    b.month,
                    f"{b.total_amount:,}",
                    self._status_from_int(b.paid_status),
                    b.paid_ymd or "",
                    b.note or "",
                ),
            )

    def on_clear(self):
        for v in (
            self.tenantName_var,
            self.roomName_var,
            self.month_var,
            self.total_var,
            self.note_var,
            self.search_var,
            self.paid_amount_var,
            self.paid_date_var,
            self.elec_prev_var,
            self.elec_curr_var,
            self.elec_price_var,
            self.water_prev_var,
            self.water_curr_var,
            self.water_price_var,
            self.room_rent_var,
            self.other_fee_var,
            self.elec_amount_var,
            self.water_amount_var,
        ):
            v.set("")
        self.status_var.set("Unpaid")
        self._selected_id = None
        self.reload()

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        self._selected_id = int(values[0])

        # lấy DTO đầy đủ từ service
        bill = self.svc._get(self._selected_id)

        self.tenantName_var.set(bill.tenant_name)
        self.roomName_var.set(bill.room_code)
        self.month_var.set(bill.month)
        self.total_var.set(str(bill.total_amount))
        self.note_var.set(bill.note or "")

        self.status_var.set(self._status_from_int(bill.paid_status))
        self.paid_amount_var.set(str(bill.paid_amount))
        self.paid_date_var.set(bill.paid_ymd or "")

        self.elec_prev_var.set("" if bill.elec_prev is None else str(bill.elec_prev))
        self.elec_curr_var.set("" if bill.elec_current is None else str(bill.elec_current))
        self.elec_price_var.set("" if bill.electric_unit_price is None else str(bill.electric_unit_price))
        self.water_prev_var.set("" if bill.water_prev is None else str(bill.water_prev))
        self.water_curr_var.set("" if bill.water_current is None else str(bill.water_current))
        self.water_price_var.set("" if bill.water_unit_price is None else str(bill.water_unit_price))
        self.room_rent_var.set("" if bill.room_rent_amount is None else str(bill.room_rent_amount))
        self.other_fee_var.set("" if bill.other_fee is None else str(bill.other_fee))

        # cập nhật amount hiển thị
        self.on_recalc()

    def on_add(self):
        if not self.tenantName_var.get().strip():
            messagebox.showwarning("Thiếu", "Customer Name is required.")
            return
        if not self.roomName_var.get().strip():
            messagebox.showwarning("Thiếu", "Room Name is required.")
            return
        if not self.month_var.get().strip():
            messagebox.showwarning("Thiếu", "Month is required.")
            return

        # nếu total đang trống thì tính lại
        if not self.total_var.get().strip():
            self.on_recalc()

        try:
            paid_amount = self._to_int(self.paid_amount_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Paid amount phải là số.")
            return

        try:
            self.svc.create(
                tenant_name=self.tenantName_var.get().strip(),
                room_code=self.roomName_var.get().strip(),
                month=self.month_var.get().strip(),
                elec_prev=self._to_int(self.elec_prev_var.get()),
                elec_current=self._to_int(self.elec_curr_var.get()),
                electric_unit_price=self._to_int(self.elec_price_var.get()),
                water_prev=self._to_int(self.water_prev_var.get()),
                water_current=self._to_int(self.water_curr_var.get()),
                water_unit_price=self._to_int(self.water_price_var.get()),
                room_rent_amount=self._to_int(self.room_rent_var.get()),
                other_fee=self._to_int(self.other_fee_var.get()),
                paid_amount=paid_amount,
                paid_status=self._status_to_int(),
                paid_ymd=self.paid_date_var.get().strip() or None,
                note=self.note_var.get().strip() or None,
            )
            self.on_clear()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_update(self):
        if not self._selected_id:
            messagebox.showinfo("Chọn", "Chọn 1 bill để update.")
            return

        try:
            paid_amount = self._to_int(self.paid_amount_var.get())
        except ValueError:
            messagebox.showerror("Lỗi", "Paid amount phải là số.")
            return

        try:
            self.svc.update(
                self._selected_id,
                tenant_name=self.tenantName_var.get().strip(),
                room_code=self.roomName_var.get().strip(),
                month=self.month_var.get().strip(),
                elec_prev=self._to_int(self.elec_prev_var.get()),
                elec_current=self._to_int(self.elec_curr_var.get()),
                electric_unit_price=self._to_int(self.elec_price_var.get()),
                water_prev=self._to_int(self.water_prev_var.get()),
                water_current=self._to_int(self.water_curr_var.get()),
                water_unit_price=self._to_int(self.water_price_var.get()),
                room_rent_amount=self._to_int(self.room_rent_var.get()),
                other_fee=self._to_int(self.other_fee_var.get()),
                paid_amount=paid_amount,
                paid_status=self._status_to_int(),
                paid_ymd=self.paid_date_var.get().strip() or None,
                note=self.note_var.get().strip() or None,
            )
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete(self):
        if not self._selected_id:
            return
        if messagebox.askyesno("Delete", "Delete this bill?"):
            try:
                self.svc.delete(self._selected_id)
                self.on_clear()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def on_export(self):
        if not self._selected_id:
            messagebox.showinfo("Export", "Chọn 1 bill để export PDF.")
            return
        try:
            path = self.svc.export_pdf(self._selected_id)
            messagebox.showinfo("Export", f"PDF đã tạo:\n{path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Export thất bại:\n{e}")