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
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=(10, 0))
        
        # Form fields
        fields_frame = ctk.CTkFrame(form, fg_color="white", corner_radius=10)
        fields_frame.pack(fill="x", pady=(0, 10))
        
        # Grid configuration for form fields
        fields_frame.grid_columnconfigure((0, 2, 4), minsize=20)
        fields_frame.grid_columnconfigure((1, 3, 5), weight=1)
        
        # Row 0
        ctk.CTkLabel(fields_frame, text="Tên khách *").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(fields_frame, textvariable=self.full_name_var, height=36, corner_radius=6).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew")
            
        ctk.CTkLabel(fields_frame, text="SĐT").grid(row=0, column=2, padx=10, pady=10, sticky="w")
        enTry_phone = ctk.CTkEntry(fields_frame, textvariable=self.phone_var, height=36, corner_radius=6)
        enTry_phone.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        enTry_phone.configure(validate="key",
                           validatecommand=(enTry_phone.register(
                               lambda s: s.isdigit() or s == ""), "%P"))
        
        ctk.CTkLabel(fields_frame, text="Giới tính").grid(row=0, column=4, padx=10, pady=10, sticky="w")
        ctk.CTkComboBox(
            fields_frame, 
            values=["Nam", "Nữ", "Khác"],
            variable=self.sex_var, 
            height=36,
            corner_radius=6,
            width=100
        ).grid(row=0, column=5, padx=5, pady=5, sticky="w")
        
        # Row 1
        ctk.CTkLabel(fields_frame, text="CCCD/CMND *").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(fields_frame, textvariable=self.id_number_var, height=36, corner_radius=6).grid(
            row=1, column=1, padx=5, pady=5, sticky="ew")
            
        ctk.CTkLabel(fields_frame, text="Ngày sinh (dd/mm/yyyy)").grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.birth_entry = ctk.CTkEntry(fields_frame, height=36, corner_radius=6, placeholder_text="dd/mm/yyyy")
        self.birth_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        self.birth_entry.bind("<FocusOut>", self._validate_birth_date)
        
        ctk.CTkLabel(fields_frame, text="Địa chỉ").grid(row=1, column=4, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(fields_frame, textvariable=self.address_var, height=36, corner_radius=6).grid(
            row=1, column=5, padx=5, pady=5, sticky="ew")
        
        # Row 2
        ctk.CTkLabel(fields_frame, text="Ghi chú").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(fields_frame, textvariable=self.note_var, height=36, corner_radius=6).grid(
            row=2, column=1, columnspan=5, padx=5, pady=5, sticky="ew")
        
        # Action buttons
        action_frame = ctk.CTkFrame(form, fg_color="transparent")
        action_frame.pack(fill="x", pady=(0, 10))
        
        # Search frame
        search_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        search_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(search_frame, text="Tìm kiếm:").pack(side="left", padx=(0, 5))
        ctk.CTkEntry(
            search_frame, 
            textvariable=self.search_var, 
            height=36, 
            corner_radius=6,
            placeholder_text="Nhập từ khóa..."
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(
            search_frame, 
            text="Tìm", 
            width=80,
            height=36,
            corner_radius=6,
            command=self.apply_search
        ).pack(side="left", padx=(0, 5))
        
        # Action buttons frame
        btn_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        # Create mode buttons
        self.btn_refresh = ctk.CTkButton(
            btn_frame, 
            text="Làm mới",
            command=self._reload,
            width=100,
            height=36,
            corner_radius=6,
            fg_color="#6c757d"
        )
        self.btn_refresh.pack(side="left", padx=5)
        
        self.btn_add = ctk.CTkButton(
            btn_frame,
            text="Thêm mới",
            command=self.on_create_tenant,
            width=100,
            height=36,
            corner_radius=6,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.btn_add.pack(side="left", padx=5)
        
        # Edit mode buttons (initially hidden)
        self.btn_update = ctk.CTkButton(
            btn_frame,
            text="Cập nhật",
            command=self.on_update_tenant,
            width=100,
            height=36,
            corner_radius=6,
            fg_color="#17a2b8",
            hover_color="#138496",
            state="disabled"
        )
        self.btn_update.pack(side="left", padx=5)
        
        self.btn_delete = ctk.CTkButton(
            btn_frame,
            text="Xóa",
            command=self.on_delete_tenant,
            width=100,
            height=36,
            corner_radius=6,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.btn_delete.pack(side="left", padx=5)
        
        # Set initial form mode
        self._set_form_mode("create")

    def _build_table(self):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Add refresh button above the table
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(
            btn_frame, 
            text="Làm mới dữ liệu",
            command=self._reload,
            width=150,
            height=30,
            corner_radius=6
        ).pack(side="right")

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
        
    def _reload(self):
        """Reload data from database"""
        self._load_data()
        self._clear_form()
        
    def _clear_form(self):
        """Clear all form fields"""
        self.current_tenant_id = None
        self.full_name_var.set("")
        self.phone_var.set("")
        self.id_number_var.set("")
        self.address_var.set("")
        self.birth_var.set("")
        self.birth_entry.delete(0, "end")
        self.sex_var.set("Nam")
        self.note_var.set("")
        
    def _validate_birth_date(self, event=None):
        """Validate and format birth date to dd/mm/yyyy"""
        date_str = self.birth_entry.get().strip()
        if not date_str:
            return
            
        # Try to parse the date
        try:
            # If it's already in yyyy-mm-dd format, convert to dd/mm/yyyy
            if '-' in date_str:
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                self.birth_var.set(date_str)  # Keep original for storage
                self.birth_entry.delete(0, "end")
                self.birth_entry.insert(0, formatted_date)
            # If it's in dd/mm/yyyy, validate it
            elif '/' in date_str:
                day, month, year = map(int, date_str.split('/'))
                if not (1 <= month <= 12 and 1 <= day <= 31 and 1900 <= year <= 2100):
                    raise ValueError("Invalid date")
                # Convert to yyyy-mm-dd for storage
                formatted_date = f"{year:04d}-{month:02d}-{day:02d}"
                self.birth_var.set(formatted_date)
        except (ValueError, IndexError):
            messagebox.showerror("Lỗi", "Định dạng ngày không hợp lệ. Vui lòng nhập theo định dạng dd/mm/yyyy")
            self.birth_entry.focus_set()
            return False
        return True

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
        
        # Get the full tenant data
        tenant = next((t for t in self.tenants_cache if t["tenant_id"] == self.current_tenant_id), None)
        if not tenant:
            return
            
        # Update form fields
        self.full_name_var.set(tenant.get("full_name", ""))
        self.phone_var.set(tenant.get("phone", ""))
        self.id_number_var.set(tenant.get("id_number", ""))
        self.address_var.set(tenant.get("address", ""))
        
        # Format birth date for display
        birth = tenant.get("birth", "")
        if birth:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(birth, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d/%m/%Y")
                self.birth_var.set(birth)  # Store in yyyy-mm-dd format
                self.birth_entry.delete(0, "end")
                self.birth_entry.insert(0, formatted_date)
            except (ValueError, TypeError):
                self.birth_var.set("")
                self.birth_entry.delete(0, "end")
        
        self.sex_var.set(self._get_sex_str(tenant.get("sex", 0)))
        self.note_var.set(tenant.get("note", ""))
        
        # Update button states
        self._set_form_mode("edit")
        self.sex_var.set(v[2])
        self.phone_var.set(v[3])
        self.id_number_var.set(v[4])
        self.address_var.set(v[5])
        self.birth_var.set(v[6])
        self.note_var.set(v[7])

    def on_create_tenant(self):
        try:
            # Validate birth date first
            if not self._validate_birth_date():
                return
                
            data = {
                "full_name": self.full_name_var.get().strip(),
                "phone": self.phone_var.get().strip(),
                "id_number": self.id_number_var.get().strip(),
                "address": self.address_var.get().strip(),
                "birth": self.birth_var.get().strip(),
                "sex": self._get_sex_int(self.sex_var.get()),
                "note": self.note_var.get().strip()
            }
            
            # Validate required fields
            if not data["full_name"]:
                messagebox.showerror("Lỗi", "Vui lòng nhập họ tên")
                return
                
            if not data["id_number"]:
                messagebox.showerror("Lỗi", "Vui lòng nhập số CMND/CCCD")
                return
                
            create_tenant(data)
            messagebox.showinfo("Thành công", "Thêm khách hàng thành công!")
            self._reload()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi thêm khách hàng: {str(e)}")

    def on_update_tenant(self):
        if not self.current_tenant_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần cập nhật")
            return
            
        try:
            # Validate birth date first
            if not self._validate_birth_date():
                return
                
            data = {
                "full_name": self.full_name_var.get().strip(),
                "phone": self.phone_var.get().strip(),
                "id_number": self.id_number_var.get().strip(),
                "address": self.address_var.get().strip(),
                "birth": self.birth_var.get().strip(),
                "sex": self._get_sex_int(self.sex_var.get()),
                "note": self.note_var.get().strip()
            }
            
            # Validate required fields
            if not data["full_name"]:
                messagebox.showerror("Lỗi", "Vui lòng nhập họ tên")
                return
                
            if not data["id_number"]:
                messagebox.showerror("Lỗi", "Vui lòng nhập số CMND/CCCD")
                return
                
            update_tenant(self.current_tenant_id, data)
            messagebox.showinfo("Thành công", "Cập nhật thông tin khách hàng thành công!")
            self._reload()
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi cập nhật thông tin: {str(e)}")

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
            self._reload()
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
