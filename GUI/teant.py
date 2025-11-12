# GUI/tenant.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from services.tenant_service import TenantService, TenantDTO

class TenantTab(ctk.CTkFrame):
    def __init__(self, parent, tenant_service: TenantService = None, room_loader=lambda: []):
        super().__init__(parent)
        self.svc = tenant_service or TenantService(get_rooms=room_loader)
        self._selected_id: int | None = None

        # ===== Form =====
        form = ctk.CTkFrame(self); form.pack(fill="x", padx=12, pady=(12,6))

        self.name_var   = ctk.StringVar()
        self.phone_var  = ctk.StringVar()
        self.email_var  = ctk.StringVar()
        self.idno_var   = ctk.StringVar()
        self.room_var   = ctk.StringVar()
        self.in_var     = ctk.StringVar()   # YYYY-MM-DD
        self.out_var    = ctk.StringVar()
        self.active_var = ctk.BooleanVar(value=True)
        self.search_var = ctk.StringVar()

        # Hàng 1
        ctk.CTkLabel(form, text="Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.name_var, width=180).grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="Phone Number").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        e_phone = ctk.CTkEntry(form, textvariable=self.phone_var, width=140)
        e_phone.grid(row=0, column=3, padx=6, pady=6)
        e_phone.configure(validate="key",
            validatecommand=(e_phone.register(lambda s: s.isdigit() or s==""), "%P"))

        ctk.CTkLabel(form, text="Room").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        self.room_cb = ctk.CTkComboBox(form, values=room_loader(), variable=self.room_var, width=120)
        self.room_cb.grid(row=0, column=5, padx=6, pady=6)

        # Hàng 2
        ctk.CTkLabel(form, text="Email").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.email_var, width=180).grid(row=1, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="ID Number").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.idno_var, width=140).grid(row=1, column=3, padx=6, pady=6)

        ctk.CTkLabel(form, text="Ngày vào (YYYY-MM-DD)").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.in_var, width=120).grid(row=1, column=5, padx=6, pady=6)

        ctk.CTkCheckBox(form, text="Đang ở", variable=self.active_var).grid(row=1, column=6, padx=6, pady=6)

        # Hàng 3: nút thao tác + tìm kiếm
        ctk.CTkButton(form, text="Add", fg_color="#27ae60", command=self.on_add).grid(row=2, column=0, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Edit",  fg_color="#f39c12", command=self.on_update).grid(row=2, column=1, padx=6, pady=(0,6))

        ctk.CTkLabel(form, text="Search").grid(row=2, column=3, padx=6, pady=(0,6), sticky="e")
        ctk.CTkEntry(form, textvariable=self.search_var, width=160).grid(row=2, column=4, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Filter", command=self.reload).grid(row=2, column=5, padx=6, pady=(0,6))
        ctk.CTkButton(form, text="Refresh", command=self.on_clear).grid(row=2, column=6, padx=6, pady=(0,6))

        # ===== Bảng =====
        table = ctk.CTkFrame(self); table.pack(fill="both", expand=True, padx=12, pady=6)
        cols = ("id","name","phone","room","in","out","status")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=14)
        self.tree.pack(side="left", fill="both", expand=True)
        headings = {
            "id":"ID", "name":"Tên", "phone":"SĐT", "room":"Phòng",
            "in":"Ngày vào", "out":"Ngày ra", "status":"Trạng thái"
        }
        widths = {"id":60,"name":180,"phone":120,"room":80,"in":100,"out":100,"status":90}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c],
                anchor=("center" if c in ("id","room","status") else "w"))
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set); sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

        # ===== Dưới cùng =====
        bottom = ctk.CTkFrame(self, fg_color="transparent"); bottom.pack(fill="x", padx=12, pady=(0,12))
        ctk.CTkButton(bottom, text="Xóa", fg_color="#e74c3c", command=self.on_delete).pack(side="right")

        self.reload()

    # ===== Helpers =====
    def reload(self):
        kw = self.search_var.get().strip() or None
        rows = self.svc.list(kw)
        self.tree.delete(*self.tree.get_children())
        for t in rows:
            self.tree.insert("", "end", values=(
                t.id, t.name, t.phone or "", t.room_code,
                t.move_in.isoformat() if t.move_in else "",
                t.move_out.isoformat() if t.move_out else "",
                "Đang ở" if t.active else "Đã rời"
            ))

    def on_clear(self):
        self._selected_id = None
        for v in (self.name_var, self.phone_var, self.email_var, self.idno_var, self.in_var, self.out_var, self.search_var):
            v.set("")
        self.active_var.set(True)
        # refresh danh sách phòng nếu cần
        try:
            self.room_cb.configure(values=self.svc._get_rooms())
        except Exception:
            pass
        self.reload()

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0], "values")
        self._selected_id = int(v[0])
        # lấy DTO để điền form
        dto = next(x for x in self.svc.list() if x.id == self._selected_id)
        self.name_var.set(dto.name)
        self.phone_var.set(dto.phone or "")
        self.email_var.set(dto.email or "")
        self.idno_var.set(dto.id_no or "")
        self.room_var.set(dto.room_code)
        self.in_var.set(dto.move_in.isoformat() if dto.move_in else "")
        self.out_var.set(dto.move_out.isoformat() if dto.move_out else "")
        self.active_var.set(dto.active)

    # ===== Actions =====
    def on_add(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Thiếu", "Nhập tên"); return
        if not self.room_var.get().strip():
            messagebox.showwarning("Thiếu", "Chọn phòng"); return
        try:
            self.svc.create(
                name=self.name_var.get().strip(),
                phone=self.phone_var.get().strip() or None,
                room_code=self.room_var.get().strip(),
                move_in=self.in_var.get().strip() or None,
                email=self.email_var.get().strip() or None,
                id_no=self.idno_var.get().strip() or None
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e)); return
        self.on_clear()

    def on_update(self):
        if self._selected_id is None:
            messagebox.showinfo("Chọn", "Chọn 1 dòng để sửa"); return
        try:
            self.svc.update(
                self._selected_id,
                name=self.name_var.get().strip(),
                phone=self.phone_var.get().strip() or None,
                room_code=self.room_var.get().strip(),
                move_in=self.in_var.get().strip() or None,
                move_out=self.out_var.get().strip() or None,
                email=self.email_var.get().strip() or None,
                id_no=self.idno_var.get().strip() or None,
                active=self.active_var.get()
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e)); return
        self.reload()

    def on_delete(self):
        if self._selected_id is None: return
        if messagebox.askyesno("Xóa", "Xóa tenant này?"):
            self.svc.delete(self._selected_id)
            self.on_clear()

    def on_move(self):
        if self._selected_id is None: return
        try:
            self.svc.move_room(self._selected_id, self.room_var.get().strip())
        except Exception as e:
            messagebox.showerror("Lỗi", str(e)); return
        self.reload()

    def on_checkout(self):
        if self._selected_id is None: return
        mvout = self.out_var.get().strip()
        if not mvout:
            messagebox.showwarning("Thiếu", "Nhập Ngày ra (YYYY-MM-DD)"); return
        try:
            self.svc.checkout(self._selected_id, mvout)
        except Exception as e:
            messagebox.showerror("Lỗi", str(e)); return
        self.reload()
