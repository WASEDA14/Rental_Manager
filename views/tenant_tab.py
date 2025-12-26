# views/tenant_tab.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

from services.tenant_service import (
    create_tenant,
    get_all_tenant,
    update_tenant,
    delete_tenant,
    validate_tenant
)


class tenantTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # ===== State =====
        self.current_tenant_id = None
        self.tenants_cache = []

        # ===== Variables =====
        self.full_name_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()
        self.id_number_var = ctk.StringVar()
        self.address_var = ctk.StringVar()
        self.birth_var = ctk.StringVar()
        self.sex_var = ctk.StringVar(value="Nam")
        self.note_var = ctk.StringVar()
        self.search_var = ctk.StringVar()

        self._build_form()
        self._build_table()
        # self._build_bottom_actions()

        self._load_data()

    # =========================================================
    # UI
    # =========================================================
    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=(12, 6))

        ctk.CTkLabel(form, text="Tên khách").grid(row=0, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.full_name_var, width=160)\
            .grid(row=0, column=1, padx=6)

        ctk.CTkLabel(form, text="SĐT").grid(row=0, column=2, sticky="w")
        enTry_phone = ctk.CTkEntry(form, textvariable=self.phone_var, width=140)
        enTry_phone.grid(row=0, column=3, padx=6)
        enTry_phone.configure(validate="key",
                           validatecommand=(enTry_phone.register(
                               lambda s: s.isdigit() or s == ""), "%P"))

        ctk.CTkLabel(form, text="Giới tính").grid(row=0, column=4, sticky="w")
        ctk.CTkComboBox(
            form, values=["Nam", "Nữ", "Khác"],
            variable=self.sex_var, width=100
        ).grid(row=0, column=5, padx=6)

        ctk.CTkLabel(form, text="CCCD/CMND").grid(row=1, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.id_number_var, width=160)\
            .grid(row=1, column=1, padx=6)

        ctk.CTkLabel(form, text="Ngày sinh").grid(row=1, column=2, sticky="w")
        DateEntry(
            form,
            textvariable=self.birth_var,
            date_pattern="dd/mm/yyyy",
            width=16
        ).grid(row=1, column=3, padx=6)

        ctk.CTkLabel(form, text="Địa chỉ").grid(row=1, column=4, sticky="w")
        ctk.CTkEntry(form, textvariable=self.address_var, width=200)\
            .grid(row=1, column=5, padx=6, columnspan=2)

        ctk.CTkLabel(form, text="Ghi chú").grid(row=2, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.note_var, width=500)\
            .grid(row=2, column=1, columnspan=6, padx=6, sticky="we")

        action = ctk.CTkFrame(form, fg_color="transparent")
        action.grid(row=3, column=0, columnspan=8, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(action, text="Search").pack(side="left")
        ctk.CTkEntry(action, textvariable=self.search_var, width=160)\
            .pack(side="left", padx=6)

        ctk.CTkButton(action, text="Tìm", width=80,
                      command=self.apply_search)\
            .pack(side="left", padx=6)

        ctk.CTkButton(action, text="Xóa khách hàng",
                      fg_color="#e74c3c",
                      command=self.on_delete_tenant) \
            .pack(side="right", padx=6)

        ctk.CTkButton(action, text="Cập nhật",
                      fg_color="#f39c12",
                      command=self.on_update_tenant)\
            .pack(side="right", padx=6)

        ctk.CTkButton(action, text="Thêm",
                      fg_color="#27ae60",
                      command=self.on_create_tenant)\
            .pack(side="right", padx=6)
            
        ctk.CTkButton(action, text="Làm mới",
                      fg_color="#7f8c8d",
                      command=self.reset_form)\
            .pack(side="right", padx=6)

    def _build_table(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "name", "sex", "phone", "idno", "address", "birth", "note")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)

        headers = {
            "id": "ID", "name": "Họ tên", "sex": "Giới tính",
            "phone": "SĐT", "idno": "CCCD",
            "address": "Địa chỉ", "birth": "Ngày sinh", "note": "Ghi chú"
        }

        widths = {
            "id": 40, "name": 150, "sex": 80, "phone": 100,
            "idno": 120, "address": 200, "birth": 100, "note": 150
        }

        for c in cols:
            self.tree.heading(c, text=headers[c])
            self.tree.column(c, width=widths[c],
                             anchor="center" if c in ("id", "sex") else "w")

        sb = ttk.Scrollbar(frame, orient="vertical",
                           command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _get_sex_int(self, text):
        return {"Nam": 0, "Nữ": 1, "Khác": 2}.get(text, 0)

    def _get_sex_str(self, val):
        return {0: "Nam", 1: "Nữ", 2: "Khác"}.get(val, "Nam")

    # =========================================================
    # Data
    # =========================================================
    def _load_data(self):
        self.tenants_cache = get_all_tenant()
        self.render_table(self.tenants_cache)

    def render_table(self, tenants):
        self.tree.delete(*self.tree.get_children())
        for r in tenants:
            self.tree.insert("", "end", values=(
                r["tenant_id"],
                r["full_name"],
                self._get_sex_str(r["sex"]),
                r["phone"] or "",
                r["id_number"],
                r["address"] or "",
                r["birth"] or "",
                r["note"] or ""
            ))

    # =========================================================
    # Search
    # =========================================================
    def apply_search(self):
        query = (self.search_var.get() or "").strip().lower()

        def match(r):
            if not query:
                return True
            haystack = " ".join([
                str(r["full_name"] or ""),
                str(r["phone"] or ""),
                str(r["id_number"] or ""),
                str(r["address"] or ""),
                str(r["birth"] or ""),
                str(r["note"] or "")
            ]).lower()
            return query in haystack

        self.render_table([r for r in self.tenants_cache if match(r)])

    # =========================================================
    # Events
    # =========================================================
    def on_select(self, _):
        sel = self.tree.selection()
        if not sel:
            return

        v = self.tree.item(sel[0], "values")
        self.current_tenant_id = int(v[0])

        self.full_name_var.set(v[1])
        self.sex_var.set(v[2])
        self.phone_var.set(v[3])
        self.id_number_var.set(v[4])
        self.address_var.set(v[5])
        self.birth_var.set(v[6])
        self.note_var.set(v[7])

    def on_create_tenant(self):
        data = self._collect_data()
        if not data:
            return
        if not data["full_name"]:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên khách hàng!")
            return
        phone = self.phone_var.get().strip()
        if phone and (len(phone) < 10 or len(phone) > 11):
            messagebox.showwarning("Lỗi", "Số điện thoại tối thiểu 10 ký tự và tối đa 11 ký tự")
            return
        if not data["id_number"]:
            messagebox.showwarning("Lỗi", "Vui lòng nhập CCCD/CMND!")
            return
        id_number = self.id_number_var.get().strip()
        if id_number and len(id_number) != 12:
            messagebox.showwarning("Lỗi", "CCCD phải đúng 12 ký tự")
            return
        if any(r["id_number"].upper() == data["id_number"].upper() for r in self.tenants_cache):
            messagebox.showwarning("Lỗi", f"Khách hàng đã tồn tại!")
            return
        try:
            create_tenant(validate_tenant(data))
            messagebox.showinfo("OK", "Thêm khách hàng thành công")
            self.reset_form()
            self._load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_update_tenant(self):
        if not self.current_tenant_id:
            messagebox.showwarning("Chưa chọn", "Chọn khách hàng trước")
            return
        data = self._collect_data()
        if not data:
            return
        if not data["full_name"]:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tên khách hàng!")
            return
        phone = self.phone_var.get().strip()
        if phone and (len(phone) < 10 or len(phone) > 11):
            messagebox.showwarning("Lỗi", "Số điện thoại tối thiểu 10 ký tự và tối đa 11 ký tự")
            return
        if not data["id_number"]:
            messagebox.showwarning("Lỗi", "Vui lòng nhập CCCD/CMND!")
            return
        id_number = self.id_number_var.get().strip()
        if id_number and len(id_number) != 12:
            messagebox.showwarning("Lỗi", "CCCD phải đúng 12 ký tự")
            return
        if any(r["id_number"].upper() == data["id_number"].upper() for r in self.tenants_cache if r["tenant_id"] != self.current_tenant_id):
            messagebox.showwarning("Lỗi", f"Khách hàng đã tồn tại!")
            return
        try:
            update_tenant(self.current_tenant_id, validate_tenant(data))
            messagebox.showinfo("OK", "Đã cập nhật")
            self.reset_form()
            self._load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete_tenant(self):
        # print(f"[DEBUG] on_delete called. Current tenant_id: {self.current_tenant_id}")
        if not self.current_tenant_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn khách hàng cần xóa!")
            return

        if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa khách hàng này?"):
            return

        try:
            delete_tenant(self.current_tenant_id)
            messagebox.showinfo("Thành công", "Đã xóa khách hàng thành công!")
            self.reset_form()
            self._load_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa khách hàng: {str(e)}")

    # =========================================================
    def reset_form(self):
        self.current_tenant_id = None
        self.full_name_var.set("")
        self.phone_var.set("")
        self.id_number_var.set("")
        self.address_var.set("")
        self.birth_var.set("")
        self.note_var.set("")
        self.sex_var.set("Nam")

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def _collect_data(self):
        return {
            "full_name": self.full_name_var.get(),
            "sex": self._get_sex_int(self.sex_var.get()),
            "phone": self.phone_var.get() or None,
            "id_number": self.id_number_var.get(),
            "address": self.address_var.get() or None,
            "birth": self.birth_var.get() or None,
            "note": self.note_var.get() or None
        }