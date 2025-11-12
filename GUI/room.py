import customtkinter as ctk
from tkinter import ttk, messagebox
from models.room_service import RoomService

class RoomTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.svc = RoomService()
        self._selected_id: int | None = None

        # ===== Form trên cùng =====
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=10, pady=(10, 6))

        self.code_var = ctk.StringVar()
        self.rent_var = ctk.StringVar()
        self.active_var = ctk.BooleanVar(value=True)
        self.search_var = ctk.StringVar()

        ctk.CTkLabel(form, text="Số phòng").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.code_var, width=160).grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="Giá thuê (VND)").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        # chỉ cho nhập số
        rent_entry = ctk.CTkEntry(form, textvariable=self.rent_var, width=160)
        rent_entry.grid(row=0, column=3, padx=6, pady=6)
        rent_entry.configure(validate="key",
            validatecommand=(rent_entry.register(lambda s: s.isdigit() or s==""), "%P"))

        ctk.CTkCheckBox(form, text="Hoạt động", variable=self.active_var).grid(row=0, column=4, padx=6, pady=6)

        self.btn_add = ctk.CTkButton(form, text="Thêm", command=self.on_add, fg_color="#27ae60")
        self.btn_add.grid(row=0, column=5, padx=6, pady=6)
        self.btn_update = ctk.CTkButton(form, text="Sửa", command=self.on_update, fg_color="#f39c12")
        self.btn_update.grid(row=0, column=6, padx=6, pady=6)

        # Dòng tìm kiếm
        ctk.CTkLabel(form, text="Tìm").grid(row=1, column=0, padx=6, pady=(0,6), sticky="w")
        search_entry = ctk.CTkEntry(form, textvariable=self.search_var, width=160)
        search_entry.grid(row=1, column=1, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Lọc", command=self.reload).grid(row=1, column=2, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Làm mới", command=self.on_clear).grid(row=1, column=3, padx=6, pady=(0,6))

        for i in range(7):
            form.grid_columnconfigure(i, weight=0)
        form.grid_columnconfigure(7, weight=1)

        # ===== Bảng danh sách =====
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("id", "code", "rent", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, side="left")

        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Số phòng")
        self.tree.heading("rent", text="Giá thuê")
        self.tree.heading("status", text="Trạng thái")
        self.tree.column("id", width=60, anchor="center")
        self.tree.column("code", width=120)
        self.tree.column("rent", width=120, anchor="e")
        self.tree.column("status", width=100, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

        # Scrollbar
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        # ===== Nút dưới cùng =====
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0,10))
        ctk.CTkButton(bottom, text="Xóa phòng", command=self.on_delete, fg_color="#e74c3c").pack(side="right", padx=6)
        ctk.CTkButton(bottom, text="Làm mới bảng", command=self.reload).pack(side="right", padx=6)

        self.reload()  # lần đầu

    # ---------- helpers ----------
    def reload(self):
        # load theo keyword
        kw = self.search_var.get().strip() or None
        rows = self.svc.list(keyword=kw)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            status = "Đang dùng" if r.is_active else "Ngưng"
            self.tree.insert("", "end", values=(r.id, r.code, f"{r.base_rent:,}", status))

    def on_clear(self):
        self.code_var.set("")
        self.rent_var.set("")
        self.active_var.set(True)
        self.search_var.set("")
        self._selected_id = None
        self.reload()

    def on_pick(self, _evt):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        self._selected_id = int(vals[0])
        self.code_var.set(vals[1])
        self.rent_var.set(vals[2].replace(",", ""))
        self.active_var.set(vals[3] == "Đang dùng")

    # ---------- actions ----------
    def on_add(self):
        code = self.code_var.get().strip()
        rent = self.rent_var.get().strip()
        if not code or not rent:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập Số phòng và Giá thuê."); return
        try:
            self.svc.create(code=code, base_rent=int(rent), is_active=self.active_var.get())
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e)); return
        self.on_clear()

    def on_update(self):
        if self._selected_id is None:
            messagebox.showinfo("Chọn dòng", "Chọn 1 phòng trong bảng để sửa."); return
        code = self.code_var.get().strip()
        rent = self.rent_var.get().strip()
        if not code or not rent:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập Số phòng và Giá thuê."); return
        try:
            self.svc.update(self._selected_id, code=code, base_rent=int(rent), is_active=self.active_var.get())
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e)); return
        self.on_clear()

    def on_delete(self):
        if self._selected_id is None:
            messagebox.showinfo("Chọn dòng", "Chọn 1 phòng để xóa."); return
        if messagebox.askyesno("Xóa phòng", f"Xóa phòng ID {self._selected_id}?"):
            self.svc.delete(self._selected_id)
            self.on_clear()
