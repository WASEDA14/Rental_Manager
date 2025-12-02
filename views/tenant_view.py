# views/tenant.py
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from models.tenant_model import TenantModel, TenantDTO

class tenantView(ctk.CTkFrame):
    def __init__(self, parent, tenant_service: TenantModel = None, room_loader=lambda: []):
        super().__init__(parent)
        self.svc = tenant_service or TenantModel()
        self._selected_id: int | None = None

        # ===== Form =====
        form = ctk.CTkFrame(self); form.pack(fill="x", padx=12, pady=(12,6))

        self.tenantName_var = ctk.StringVar()
        self.phone_var  = ctk.StringVar()
        self.email_var  = ctk.StringVar()
        self.idNumber_var   = ctk.StringVar()
        self.room_var   = ctk.StringVar()
        self.in_var     = ctk.StringVar()
        self.out_var    = ctk.StringVar()
        self.note_var = ctk.StringVar()
        self.active_var = ctk.BooleanVar(value=True)
        self.search_var = ctk.StringVar()

        # Hàng 1
        ctk.CTkLabel(form, text="Customer Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.tenantName_var, width=160).grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(form, text="Phone Number").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        e_phone = ctk.CTkEntry(form, textvariable=self.phone_var, width=140)
        e_phone.grid(row=0, column=3, padx=6, pady=6)
        e_phone.configure(validate="key",
            validatecommand=(e_phone.register(lambda s: s.isdigit() or s==""), "%P"))

        ctk.CTkLabel(form, text="Room").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.room_var, width=160).grid(row=0, column=5, padx=6, pady=6, sticky="w")

        # Hàng 2
        ctk.CTkLabel(form, text="Email").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.email_var, width=160).grid(row=1, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="ID Number").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.idNumber_var, width=140).grid(row=1, column=3, padx=6, pady=6, )



        ctk.CTkLabel(form, text="Day in").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        in_date = DateEntry(
            form,
            textvariable=self.in_var,
            width=16,
            date_pattern="yyyy-mm-dd",
            foreground="black",  # màu chữ ngày
            background="white",  # nền calendar
            selectbackground="blue",  # nền ngày được chọn
            selectforeground="white",
        )
        in_date.grid(row=1, column=5, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(form, text="Day out").grid(row=1, column=6, padx=6, pady=6, sticky="w")
        out_date = DateEntry(
            form,
            textvariable=self.out_var,
            width=16,
            date_pattern="yyyy-mm-dd",
            foreground="black",  # màu chữ ngày
            background="white",  # nền calendar
            selectbackground="blue",  # nền ngày được chọn
            selectforeground="white",
        )
        out_date.grid(row=1, column=7, padx=6, pady=6, sticky="w")

        ctk.CTkCheckBox(form, text="Đang ở", variable=self.active_var).grid(row=1, column=8, padx=6, pady=6 )

        ctk.CTkLabel(form, text="Note").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.note_var, width=300).grid(row=2, column=1, padx=6, pady=6, columnspan=7,
                                                                       sticky="we")

        # Hàng 3: nút thao tác + tìm kiếm
        ctk.CTkLabel(form, text="Search").grid(row=3, column=0, padx=6, pady=(0, 6), sticky="w")
        ctk.CTkEntry(form, textvariable=self.search_var, width=160).grid(row=3, column=1, padx=6, pady=(0, 6), sticky="w")

        ctk.CTkButton(form, text="Search", command=self.reload).grid(row=3, column=2, padx=6, pady=(0, 6))

        ctk.CTkButton(form, text="Clear", command=self.on_clear).grid(row=3, column=3, padx=6, pady=(0, 6))

        ctk.CTkButton(form, text="Add", fg_color="#27ae60", command=self.on_add).grid(row=3, column=4, padx=6, pady=(0,6))

        ctk.CTkButton(form, text="Update",  fg_color="#f39c12", command=self.on_update).grid(row=3, column=5, padx=6, pady=(0,6))


        # ===== Bảng =====
        table = ctk.CTkFrame(self); table.pack(fill="both", expand=True, padx=12, pady=6)
        cols = ("id","name","phone","room","in","out","status","note")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=14)
        self.tree.pack(side="left", fill="both", expand=True)
        headings = {
            "id":"ID", "name":"Tên", "phone":"SĐT", "room":"Phòng",
            "in":"Ngày vào", "out":"Ngày ra", "status":"Trạng thái","note" :"Note"
        }
        widths = {"id":60,"name":50,"phone":50,"room":50,"in":100,"out":100,"status":90, "note": 120}
        for c in cols:
            self.tree.heading(c, text=headings[c])
            self.tree.column(c, width=widths[c],
                             anchor=("center" if c in ("id","room", 'status') else "w"))
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
            status_text = "Đang ở" if t.is_deleted == 0 else "Đã rời"
            self.tree.insert("", "end", values=(
                t.id, t.name, t.phone or "", t.room_no,
                t.move_in.isoformat() if t.move_in else "",
                t.move_out.isoformat() if t.move_out else "",
                status_text,

            ))

    def on_clear(self):
        self._selected_id = None
        for v in (self.tenantName_var, self.phone_var, self.email_var, self.idNumber_var, self.in_var, self.out_var, self.search_var, self.room_var, self.note_var):
            v.set("")
        self.active_var.set(True)
        # refresh danh sách phòng nếu cần
        try:
            self.room.configure(values=self.svc._get_rooms())
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
        self.tenantName_var.set(dto.name)
        self.phone_var.set(dto.phone or "")
        self.email_var.set(dto.email or "")
        self.idNumber_var.set(dto.id_number or "")
        self.room_var.set(dto.room_no)
        self.in_var.set(dto.move_in.isoformat() if dto.move_in else "")
        self.out_var.set(dto.move_out.isoformat() if dto.move_out else "")
        self.active_var.set(dto.is_deleted == 0)

    # ===== Actions =====
    def on_add(self):
        if not self.tenantName_var.get().strip():
            messagebox.showwarning("Thiếu", "Nhập tên");
            return
        if not self.room_var.get().strip():
            messagebox.showwarning("Thiếu", "Chọn phòng");
            return

        move_in = self.in_var.get().strip() or None
        move_out = self.out_var.get().strip() or None

        try:
            self.svc.create(
                full_name=self.tenantName_var.get().strip(),
                phone=self.phone_var.get().strip() or None,
                room_no=self.room_var.get().strip(),
                move_in=move_in,
                move_out=move_out,  # 👈 thêm
                email=self.email_var.get().strip() or None,
                id_number=self.idNumber_var.get().strip() or None,
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self.on_clear()

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


    def on_update(self):
        if self._selected_id is None:
            messagebox.showinfo("Chọn", "Chọn 1 dòng để sửa")
            return

        try:
            self.svc.update(
                self._selected_id,
                full_name=self.tenantName_var.get().strip(),
                phone=self.phone_var.get().strip() or None,
                room_no=self.room_var.get().strip(),
                move_in=self.in_var.get().strip() or None,
                move_out=self.out_var.get().strip() or None,
                email=self.email_var.get().strip() or None,
                id_number=self.idNumber_var.get().strip() or None,
                active=self.active_var.get(),
            )
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self.reload()
