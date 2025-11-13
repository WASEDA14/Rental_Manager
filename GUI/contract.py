# GUI/contract.py
import customtkinter as ctk
from tkinter import ttk, messagebox

STATUSES = ["Draft", "Active", "Ended", "Canceled"]

class ContractTab(ctk.CTkFrame):
    def __init__(self, parent,
                 service=None,                   # inject ContractService sau
                 load_tenants=lambda: [],        # -> ["Nguyễn A (#1)", ...]
                 load_rooms=lambda: []):         # -> ["R101", "R102", ...]
        super().__init__(parent)
        self.svc = service
        self._selected_id = None

        # ========== FORM ==========
        form = ctk.CTkFrame(self); form.pack(fill="x", padx=12, pady=(12,6))

        self.contract_no = ctk.StringVar()
        self.tenant_var  = ctk.StringVar()
        self.room_var    = ctk.StringVar()
        self.start_var   = ctk.StringVar()
        self.end_var     = ctk.StringVar()
        self.term_var    = ctk.StringVar()
        self.rent_var    = ctk.StringVar()
        self.deposit_var = ctk.StringVar()
        self.billday_var = ctk.StringVar(value="5")
        self.elec_var    = ctk.StringVar()
        self.water_var   = ctk.StringVar()
        self.service_var = ctk.StringVar(value="0")
        self.status_var  = ctk.StringVar(value="Draft")
        self.search_var  = ctk.StringVar()

        # validator số nguyên
        def v_int(s): return s.isdigit() or s == ""
        vcmd = self.register(v_int)

        # Cột trái
        r = 0
        ctk.CTkLabel(form, text="Contract No").grid(row=r, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.contract_no, width=150, state="readonly").grid(row=r, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="Tenant").grid(row=r, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.tenant_var, width=150).grid(row=0, column=3, padx=6, pady=6)

        ctk.CTkLabel(form, text="Room").grid(row=r, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.room_var, width=150).grid(row=0, column=5, padx=6, pady=6)

        r += 1
        ctk.CTkLabel(form, text="Start").grid(row=r, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.start_var, width=150).grid(row=r, column=1, padx=6, pady=6)
        ctk.CTkLabel(form, text="End").grid(row=r, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.end_var, width=150).grid(row=r, column=3, padx=6, pady=6)
        ctk.CTkLabel(form, text="Term").grid(row=r, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.term_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=5, padx=6, pady=6)

        r += 1
        ctk.CTkLabel(form, text="Base Rent (VND)").grid(row=r, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.rent_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=1, padx=6, pady=6)
        ctk.CTkLabel(form, text="Deposit (VND)").grid(row=r, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.deposit_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=3, padx=6, pady=6)
        ctk.CTkLabel(form, text="Billing Day").grid(row=r, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.billday_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=5, padx=6, pady=6)

        r += 1
        ctk.CTkLabel(form, text="Electric (VND/kWh)").grid(row=r, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.elec_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=1, padx=6, pady=6)
        ctk.CTkLabel(form, text="Water (VND/m³)").grid(row=r, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.water_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=3, padx=6, pady=6)
        ctk.CTkLabel(form, text="Service Fee (VND)").grid(row=r, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.service_var, width=150,
                     validate="key", validatecommand=(vcmd, "%P")).grid(row=r, column=5, padx=6, pady=6)

        r += 1
        ctk.CTkLabel(form, text="Status").grid(row=r, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkComboBox(form, values=STATUSES, variable=self.status_var, width=150, state="readonly").grid(row=r, column=1, padx=6, pady=6)

        # Tool bar
        toolbar = ctk.CTkFrame(self, fg_color="transparent"); toolbar.pack(fill="x", padx=12, pady=(0,6))
        ctk.CTkButton(toolbar, text="Add",  command=self.on_new).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Save", command=self.on_save, fg_color="#27ae60").pack(side="left", padx=4)
        # ctk.CTkButton(toolbar, text="Activate", command=self.on_activate).pack(side="left", padx=4)
        # ctk.CTkButton(toolbar, text="Extend",   command=self.on_extend).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="End",      command=self.on_end, fg_color="#e67e22").pack(side="left", padx=4)
        # ctk.CTkButton(toolbar, text="Suspend/Resume", command=self.on_toggle_suspend).pack(side="left", padx=4)
        ctk.CTkButton(toolbar, text="Delete",   command=self.on_delete, fg_color="#e74c3c").pack(side="left", padx=4)

        # Search
        ctk.CTkLabel(toolbar, text="").pack(side="right", padx=(0,6))
        ctk.CTkEntry(toolbar, textvariable=self.search_var, width=180).pack(side="right", padx=6)

        # ========== TABLE ==========
        table = ctk.CTkFrame(self); table.pack(fill="both", expand=True, padx=12, pady=(6,12))
        cols = ("id","no","tenant","room","start","end","rent","deposit","status")
        self.tree = ttk.Treeview(table, columns=cols, show="headings", height=14)
        for c,t,w in [
            ("id","ID",50),("no","No",110),("tenant","Tenant",180),("room","Room",80),
            ("start","Start",100),("end","End",100),("rent","Rent",100),("deposit","Deposit",100),
            ("status","Status",100)
        ]:
            self.tree.heading(c, text=t)
            self.tree.column(c, width=w, anchor="center" if c in ("id","room","status") else "w")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set); sb.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

        self.reload()

    # ===== Helpers/UI =====
    def _form_data(self):
        return dict(
            contract_no=self.contract_no.get() or None,
            tenant=self.tenant_var.get().strip(),
            room=self.room_var.get().strip(),
            start=self.start_var.get().strip(),
            end=self.end_var.get().strip() or None,
            term=self.term_var.get().strip() or None,
            base_rent=int(self.rent_var.get() or 0),
            deposit=int(self.deposit_var.get() or 0),
            billing_day=int(self.billday_var.get() or 5),
            elec=int(self.elec_var.get() or 0),
            water=int(self.water_var.get() or 0),
            service=int(self.service_var.get() or 0),
            status=self.status_var.get(),
        )

    def _fill_form(self, row):
        self._selected_id = row["id"]
        self.contract_no.set(row.get("contract_no",""))
        self.tenant_var.set(row.get("tenant",""))
        self.room_var.set(row.get("room",""))
        self.start_var.set(row.get("start",""))
        self.end_var.set(row.get("end","") or "")
        self.term_var.set(str(row.get("term","") or ""))
        self.rent_var.set(str(row.get("base_rent",0)))
        self.deposit_var.set(str(row.get("deposit",0)))
        self.billday_var.set(str(row.get("billing_day",5)))
        self.elec_var.set(str(row.get("elec",0)))
        self.water_var.set(str(row.get("water",0)))
        self.service_var.set(str(row.get("service",0)))
        self.status_var.set(row.get("status","Draft"))

    def on_new(self):
        self._selected_id = None
        for v in [self.contract_no,self.tenant_var,self.room_var,self.start_var,self.end_var,
                  self.term_var,self.rent_var,self.deposit_var,self.billday_var,
                  self.elec_var,self.water_var,self.service_var]:
            v.set("")
        self.status_var.set("Draft")

    def reload(self):
        self.tree.delete(*self.tree.get_children())
        rows = self.svc.list(self.search_var.get().strip()) if self.svc else []
        for r in rows:
            self.tree.insert("", "end", values=(
                r["id"], r["contract_no"], r["tenant"], r["room"],
                r["start"], r.get("end",""), f"{r['base_rent']:,}", f"{r['deposit']:,}", r["status"]
            ))

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        # giả định self.svc.get(id) trả dict; nếu chưa có service, bạn map từ vals:
        if self.svc and hasattr(self.svc, "get"):
            self._fill_form(self.svc.get(int(vals[0])))
        else:
            self._fill_form(dict(
                id=int(vals[0]), contract_no=vals[1], tenant=vals[2], room=vals[3],
                start=vals[4], end=vals[5] or "", base_rent=int(vals[6].replace(",","")),
                deposit=int(vals[7].replace(",","")), status=vals[8]
            ))

    # ===== Actions (nối service sau) =====
    def on_save(self):
        if not self.svc:
            messagebox.showinfo("Demo", "Chưa gắn ContractService."); return
        data = self._form_data()
        try:
            if self._selected_id is None:
                self.svc.create(**data)
            else:
                self.svc.update(self._selected_id, **data)
            self.reload(); self.on_new()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_activate(self):
        if not self._selected_id or not self.svc: return
        try:
            self.svc.activate(self._selected_id)
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_extend(self):
        if not self._selected_id or not self.svc: return
        # ví dụ: thêm 6 tháng
        try:
            self.svc.extend(self._selected_id, extra_months=6)
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_end(self):
        if not self._selected_id or not self.svc: return
        try:
            self.svc.end(self._selected_id)   # hoặc truyền end_date nếu service yêu cầu
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_toggle_suspend(self):
        if not self._selected_id or not self.svc: return
        try:
            self.svc.toggle_suspend(self._selected_id)  # implement trong service
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete(self):
        if not self._selected_id or not self.svc: return
        if messagebox.askyesno("Xóa", "Xóa hợp đồng này?"):
            try:
                self.svc.delete(self._selected_id)
                self.reload(); self.on_new()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
