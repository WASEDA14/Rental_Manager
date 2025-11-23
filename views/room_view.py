import customtkinter as ctk
from tkinter import ttk, messagebox


from models.room_model import RoomModel

class roomView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.svc = RoomModel()
        # room_id là TEXT nên để str, không phải int
        self._selected_id: str | None = None

        # ===== Form trên cùng =====
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=10, pady=(10, 6))

        self.roomName_var = ctk.StringVar()
        self.rent_var = ctk.StringVar()
        self.electric_var = ctk.StringVar()
        self.water_var = ctk.StringVar()
        self.active_var = ctk.BooleanVar(value=True)
        self.search_var = ctk.StringVar()
        self.note_var = ctk.StringVar()

        ctk.CTkLabel(form, text="Room Name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.roomName_var, width=160).grid(row=0, column=1, padx=6, pady=6,sticky="w")

        ctk.CTkLabel(form, text="Rent Amount (VND)").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        # chỉ cho nhập số
        rent_entry = ctk.CTkEntry(form, textvariable=self.rent_var, width=160)
        rent_entry.grid(row=0, column=3, padx=6, pady=6,sticky="w")
        rent_entry.configure(
            validate="key",
            validatecommand=(rent_entry.register(lambda s: s.isdigit() or s == ""), "%P")
        )

        ctk.CTkLabel(form, text="Electric Unit Price").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        # chỉ cho nhập số
        electric_entry = ctk.CTkEntry(form, textvariable=self.electric_var, width=160)
        electric_entry.grid(row=0, column=5, padx=6, pady=6,sticky="w")
        electric_entry.configure(
            validate="key",
            validatecommand=(electric_entry.register(lambda s: s.isdigit() or s == ""), "%P")
        )


        ctk.CTkLabel(form, text="Water Unit Price").grid(row=0, column=6, padx=6, pady=6, sticky="w")
        # chỉ cho nhập số
        water_entry = ctk.CTkEntry(form, textvariable=self.water_var, width=160)
        water_entry.grid(row=0, column=7, padx=6, pady=6,sticky="w")
        water_entry.configure(
            validate="key",
            validatecommand=(water_entry.register(lambda s: s.isdigit() or s == ""), "%P"))

        ctk.CTkLabel(form, text="Note").grid(row=1, column=0, padx=6, pady=6, sticky = "w" )
        ctk.CTkEntry(form, textvariable=self.note_var, width=300).grid(row=1, column=1, padx=6, pady=6, columnspan=7,sticky="we")


        ctk.CTkCheckBox(form, text="Active", variable=self.active_var).grid(
            row=2, column=4, padx=6, pady=6)

        self.btn_add = ctk.CTkButton(form, text="Add", command=self.on_add, fg_color="#27ae60")
        self.btn_add.grid(row=2, column=5, padx=6, pady=(0, 6), sticky="we")
        self.btn_update = ctk.CTkButton(form, text="Update", command=self.on_update, fg_color="#f39c12")
        self.btn_update.grid(row=2, column=6, padx=6, pady=(0, 6), sticky="we")

        # Dòng tìm kiếm
        ctk.CTkLabel(form, text="Search").grid(row=2, column=0, padx=6, pady=(0, 6), sticky="w")
        search_entry = ctk.CTkEntry(form, textvariable=self.search_var, width=160)
        search_entry.grid(row=2, column=1, padx=6, pady=(0, 6), sticky="we")
        ctk.CTkButton(form, text="Search", command=self.reload).grid(
            row=2, column=2, padx=6, pady=(0, 6), sticky="we"
        )
        ctk.CTkButton(form, text="Clear", command=self.on_clear).grid(
            row=2, column=3, padx=6, pady=(0, 6), sticky="we"
        )

        for i in range(8):
            form.grid_columnconfigure(i, weight=1)

        # ===== Bảng danh sách =====
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("id", "roomName", "rent", "status","electricUnitPrice","waterUnitPrice","note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.pack(fill="both", expand=True, side="left")

        self.tree.heading("id", text="ID")
        self.tree.heading("roomName", text="Room Name")
        self.tree.heading("rent", text="Rent Amount")
        self.tree.heading("electricUnitPrice", text="Electric Unit Price")
        self.tree.heading("waterUnitPrice", text="Water Unit Price")
        self.tree.heading("status", text="Status")
        self.tree.heading("note", text="Note")
        self.tree.column("id", width=5, anchor="center")
        self.tree.column("roomName", width=50)
        self.tree.column("rent", width=90, anchor="e")
        self.tree.column("electricUnitPrice", width=65, anchor="e")
        self.tree.column("waterUnitPrice", width=65, anchor="e")
        self.tree.column("status", width=50, anchor="center")
        self.tree.column("note", width=150, anchor="w")


        self.tree.bind("<<TreeviewSelect>>", self.on_pick)


        # Scrollbar
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        # ===== Nút dưới cùng =====
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(
            bottom, text="Delete", command=self.on_delete, fg_color="#e74c3c"
        ).pack(side="right", padx=6)
        ctk.CTkButton(bottom, text="Refresh", command=self.reload).pack(side="right", padx=6)

        self.reload()  # lần đầu

    # ---------- helpers ----------
    def reload(self):
        kw = self.search_var.get().strip() or None
        rows = self.svc.list(keyword=kw)
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            active = (r.status == 1) and (r.is_deleted == 0)
            status_text = "Available" if active else "Unavailable"
            self.tree.insert(
                "",
                "end",
                values=(
                    r.room_id,
                    r.room_name,
                    f"{r.base_rent:,}",
                    status_text,
                    r.electric_unit_price,
                    r.water_unit_price,
                    r.note,
                ),
            )

    def on_clear(self):
        self.roomName_var.set("")
        self.rent_var.set("")
        self.electric_var.set("")
        self.water_var.set("")
        self.note_var.set("")
        self.rent_var.set("")
        self.active_var.set(True)
        self.search_var.set("")
        self._selected_id = None
        self.reload()

    def on_add(self):
            roomName = self.roomName_var.get().strip()
            rent = self.rent_var.get().strip()
            electric = self.electric_var.get().strip()
            water = self.water_var.get().strip()
            note = self.note_var.get().strip()

            if not roomName:
                messagebox.showwarning("Room Name is required", "Please input the Room Name.")
                return
            if not rent:
                messagebox.showwarning("Rent Amount is required", "Please input the Rent Amount.")
                return

             # CHECK TRÙNG ROOM NAME
            for item_id in self.tree.get_children():
                values = self.tree.item(item_id, "values")
                existing_name = values[1]  # cột 1 = roomName
                if existing_name == roomName:
                    messagebox.showwarning(
                        "Duplicate Room Name",
                        f"Room name '{roomName}' already exists."
                    )
                    return
            # --------------------------------------

            try:
                base_rent = int(rent)
                electric_unit = int(electric) if electric else None
                water_unit = int(water) if water else None
            except ValueError:
                messagebox.showerror("Lỗi", "Rent / Electric / Water phải là số.")
                return

            self.svc.create(
                room_name=roomName,
                base_rent=base_rent,
                electric_unit_price=electric_unit,
                water_unit_price=water_unit,
                note=note,
                is_active=self.active_var.get(),
            )

            self.on_clear()

    def on_update(self):
        if self._selected_id is None:
            messagebox.showinfo("Chọn dòng", "Chọn 1 phòng trong bảng để sửa.")
            return

        roomName = self.roomName_var.get().strip()
        rent = self.rent_var.get().strip()
        electric = self.electric_var.get().strip()
        water = self.water_var.get().strip()
        note = self.note_var.get().strip()

        if not roomName or not rent:
            messagebox.showwarning("Thiếu dữ liệu", "Nhập Room Name và Rent Amount.")
            return

        try:
            base_rent = int(rent)
            electric_unit = int(electric) if electric else None
            water_unit = int(water) if water else None
        except ValueError:
            messagebox.showerror("Lỗi", "Rent / Electric / Water phải là số.")
            return

        try:
            self.svc.update(
                room_id=self._selected_id,
                room_name=roomName,
                base_rent=base_rent,
                electric_unit_price=electric_unit,
                water_unit_price=water_unit,
                floor=None,  # hoặc lấy từ 1 biến khác nếu có
                is_active=self.active_var.get(),
                note=note,
                area_m2=None,  # hoặc từ 1 biến khác nếu có
            )
        except ValueError as e:
            messagebox.showerror("Lỗi", str(e))
            return

        self.on_clear()

    def on_delete(self):
        if self._selected_id is None:
            messagebox.showinfo("Chọn dòng", "Chọn 1 phòng để xóa.")
            return

        if messagebox.askyesno("Xóa phòng", f"Xóa phòng ID {self._selected_id}?"):
            try:
                self.svc.delete(self._selected_id)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa phòng:\n{e}")
                return
            self.on_clear()


    def on_pick(self, event):
        selected = self.tree.selection()
        if not selected:
            self._selected_id = None
            return

        item_id = selected[0]
        values = self.tree.item(item_id, "values")

        # cột 0 là ID
        self._selected_id = values[0]

        # fill form nếu muốn
        self.roomName_var.set(values[1])  # roomName
        self.rent_var.set(str(values[2]).replace(",", ""))  # rent
        self.electric_var.set("" if values[4] is None else str(values[4]))
        self.water_var.set("" if values[5] is None else str(values[5]))
        self.note_var.set("" if values[6] is None else str(values[6]))



