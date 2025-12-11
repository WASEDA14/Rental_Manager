# views/tenant.py
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from services.tenant_service import (
    create_tenant,
    get_all_tenant,
    get_tennant_by_id,
    update_tenant,
    delete_tenant,
    validate_tenant
)
from datetime import datetime


class tenantTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._selected_id: int | None = None

        # ===== Variables =====
        self.full_name_var = ctk.StringVar()
        self.phone_var = ctk.StringVar()
        self.id_number_var = ctk.StringVar()
        self.address_var = ctk.StringVar()
        self.birth_var = ctk.StringVar()
        self.sex_var = ctk.StringVar(value="Nam")  # Default value
        self.note_var = ctk.StringVar()
        self.search_var = ctk.StringVar()

        # ===== Form Layout =====
        self._build_form()

        # ===== Table Layout =====
        self._build_table()

        # ===== Action Buttons =====
        self._build_bottom_actions()

        # Load initial data
        self.reload()

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=(12, 6))

        # --- Row 0 ---
        ctk.CTkLabel(form, text="Full Name *").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.full_name_var, width=160).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(form, text="Phone").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        e_phone = ctk.CTkEntry(form, textvariable=self.phone_var, width=140)
        e_phone.grid(row=0, column=3, padx=6, pady=6)
        # Validation for phone (digits only)
        e_phone.configure(validate="key", validatecommand=(e_phone.register(lambda s: s.isdigit() or s == ""), "%P"))

        ctk.CTkLabel(form, text="Sex").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkComboBox(form, values=["Nam", "Nữ", "Khác"], variable=self.sex_var, width=100).grid(row=0, column=5,
                                                                                                   padx=6, pady=6,
                                                                                                   sticky="w")

        # --- Row 1 ---
        ctk.CTkLabel(form, text="ID Number *").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.id_number_var, width=160).grid(row=1, column=1, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(form, text="Birth Date").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        DateEntry(
            form,
            textvariable=self.birth_var,
            width=16,
            date_pattern="yyyy-mm-dd",
            foreground="black",
            background="white",
            selectbackground="blue",
            selectforeground="white",
        ).grid(row=1, column=3, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(form, text="Address").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.address_var, width=200).grid(row=1, column=5, padx=6, pady=6, sticky="w",
                                                                          columnspan=2)

        # --- Row 2 ---
        ctk.CTkLabel(form, text="Note").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.note_var, width=500).grid(row=2, column=1, padx=6, pady=6, columnspan=6,
                                                                       sticky="we")

        # --- Row 3 (Actions) ---
        action_frame = ctk.CTkFrame(form, fg_color="transparent")
        action_frame.grid(row=3, column=0, columnspan=8, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(action_frame, text="Search:").pack(side="left", padx=(6, 2))
        ctk.CTkEntry(action_frame, textvariable=self.search_var, width=160).pack(side="left", padx=2)
        ctk.CTkButton(action_frame, text="Search", command=self.reload, width=80).pack(side="left", padx=6)
        ctk.CTkButton(action_frame, text="Clear", command=self.on_clear, width=80, fg_color="gray").pack(side="left",
                                                                                                         padx=6)

        ctk.CTkButton(action_frame, text="Update", fg_color="#f39c12", command=self.on_update, width=80).pack(
            side="right", padx=6)
        ctk.CTkButton(action_frame, text="Add", fg_color="#27ae60", command=self.on_add, width=80).pack(side="right",
                                                                                                        padx=6)

    def _build_table(self):
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "full_name", "sex", "phone", "id_number", "address", "birth", "note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        headings = {
            "id": "ID", "full_name": "Họ Tên", "sex": "Giới tính",
            "phone": "SĐT", "id_number": "CCCD/CMND", "address": "Địa chỉ",
            "birth": "Ngày sinh", "note": "Ghi chú"
        }
        widths = {
            "id": 40, "full_name": 150, "sex": 60, "phone": 100,
            "id_number": 120, "address": 200, "birth": 100, "note": 150
        }

        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c], anchor=("center" if c in ("id", "sex") else "w"))

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

    def _build_bottom_actions(self):
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(bottom, text="Xóa Tenant", fg_color="#e74c3c", command=self.on_delete).pack(side="right")

    # ===== Helpers =====

    def _get_sex_int(self, text):
        return {"Nam": 0, "Nữ": 1, "Khác": 2}.get(text, 0)

    def _get_sex_str(self, val):
        return {0: "Nam", 1: "Nữ", 2: "Khác"}.get(val, "Nam")

    def reload(self):
        # Lấy dữ liệu từ BE
        rows = get_all_tenant()

        # Filter nếu có từ khóa tìm kiếm
        kw = self.search_var.get().strip().lower()
        if kw:
            rows = [r for r in rows if kw in str(r['full_name']).lower() or kw in str(r['phone'])]

        # Clear bảng cũ
        self.tree.delete(*self.tree.get_children())

        # Insert dữ liệu mới
        for r in rows:
            self.tree.insert("", "end", values=(
                r['tenant_id'],
                r['full_name'],
                self._get_sex_str(r['sex']),
                r['phone'] or "",
                r['id_number'],
                r['address'] or "",
                r['birth'] or "",
                r['note'] or ""
            ))

    def on_clear(self):
        self._selected_id = None
        self.full_name_var.set("")
        self.phone_var.set("")
        self.id_number_var.set("")
        self.address_var.set("")
        self.birth_var.set("")
        self.note_var.set("")
        self.sex_var.set("Nam")
        self.search_var.set("")

        # Bỏ chọn trên bảng
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel:
            return

        # Lấy giá trị từ dòng đã chọn trên bảng
        v = self.tree.item(sel[0], "values")
        self._selected_id = int(v[0])

        # Gọi BE lấy chi tiết (để đảm bảo dữ liệu mới nhất) hoặc dùng luôn dữ liệu trên bảng
        # Ở đây dùng luôn dữ liệu trên bảng cho nhanh, trừ khi cần dữ liệu ẩn
        self.full_name_var.set(v[1])
        self.sex_var.set(v[2])
        self.phone_var.set(v[3])
        self.id_number_var.set(v[4])
        self.address_var.set(v[5])
        self.birth_var.set(v[6])
        self.note_var.set(v[7])

    # ===== Actions =====

    def on_add(self):
        # 1. Thu thập dữ liệu thô
        raw_data = {
            "full_name": self.full_name_var.get(),
            "sex": self._get_sex_int(self.sex_var.get()),
            "phone": self.phone_var.get() or None,
            "id_number": self.id_number_var.get(),
            "address": self.address_var.get() or None,
            "birth": self.birth_var.get() or None,
            "note": self.note_var.get() or None
        }

        # 2. Validate & Thực thi
        try:
            # Validate dữ liệu (logic BE)
            valid_data = validate_tenant(raw_data)

            # Gọi API tạo mới
            create_tenant(valid_data)

            messagebox.showinfo("Thành công", "Đã thêm khách thuê mới!")
            self.on_clear()
            self.reload()

        except ValueError as ve:
            messagebox.showerror("Lỗi dữ liệu", str(ve))
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể thêm: {e}")

    def on_update(self):
        if self._selected_id is None:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách thuê cần sửa!")
            return

        # 1. Thu thập dữ liệu
        raw_data = {
            "full_name": self.full_name_var.get(),
            "sex": self._get_sex_int(self.sex_var.get()),
            "phone": self.phone_var.get() or None,
            "id_number": self.id_number_var.get(),
            "address": self.address_var.get() or None,
            "birth": self.birth_var.get() or None,
            "note": self.note_var.get() or None
        }

        # 2. Validate & Thực thi
        try:
            valid_data = validate_tenant(raw_data)

            update_tenant(self._selected_id, valid_data)

            messagebox.showinfo("Thành công", "Cập nhật thành công!")
            self.on_clear()
            self.reload()

        except ValueError as ve:
            messagebox.showerror("Lỗi dữ liệu", str(ve))
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể cập nhật: {e}")

    def on_delete(self):
        if self._selected_id is None:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn khách thuê cần xóa!")
            return

        if not messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa khách thuê này?"):
            return

        try:
            delete_tenant(self._selected_id)
            messagebox.showinfo("Thành công", "Đã xóa khách thuê!")
            self.on_clear()
            self.reload()
        except ValueError as ve:
            # Lỗi nghiệp vụ từ BE (ví dụ: đang có hợp đồng)
            messagebox.showerror("Không thể xóa", str(ve))
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))