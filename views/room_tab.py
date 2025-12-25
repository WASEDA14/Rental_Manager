import customtkinter as ctk
from tkinter import ttk, messagebox
from services.room_service import get_all_rooms, create_room, update_room, delete_room
from utils.format import parse_currency, format_currency, format_money

STATUS_MAP = {
    "Trống": 0,
    "Đang thuê": 1,
    "Đang chuẩn bị": 2
}
# Map ngược để hiển thị lên bảng: {0: "Trống", ...}
STATUS_MAP_REV = {v: k for k, v in STATUS_MAP.items()}


class roomTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.current_room_id = None

        # Biến cache để lưu danh sách phòng (giúp check trùng tên nhanh hơn)
        self.rooms_cache = []
        
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # Title and action buttons
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(10, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Quản lý phòng",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        self.btn_refresh = ctk.CTkButton(
            btn_frame, 
            text="Làm mới",
            command=self.reset_form,
            width=100,
            height=36,
            corner_radius=8
        )
        self.btn_refresh.pack(side="left", padx=5)
        
        self.btn_add = ctk.CTkButton(
            btn_frame,
            text="Thêm mới",
            command=self.add_room,
            width=100,
            height=36,
            corner_radius=8,
            fg_color="#28a745",
            hover_color="#218838"
        )
        self.btn_add.pack(side="left", padx=5)
        
        self.btn_update = ctk.CTkButton(
            btn_frame,
            text="Cập nhật",
            command=self.update_room,
            width=100,
            height=36,
            corner_radius=8,
            fg_color="#17a2b8",
            hover_color="#138496",
            state="disabled"
        )
        self.btn_update.pack(side="left", padx=5)
        
        self.btn_delete = ctk.CTkButton(
            btn_frame,
            text="Xóa",
            command=self.delete_room,
            width=100,
            height=36,
            corner_radius=8,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.btn_delete.pack(side="left", padx=5)

        # Form frame
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=20, pady=20)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="form_cols")

        # Form fields - Row 1
        ctk.CTkLabel(form, text="Tên phòng *").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_name = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_name.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(form, text="Số tầng").grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.entry_floor = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_floor.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(form, text="Diện tích (m²)").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.entry_area = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_area.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(form, text="Giá thuê (VNĐ)").grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.entry_rent = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_rent.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        self.entry_rent.bind("<KeyRelease>", lambda e: format_money(self, e))

        # Form fields - Row 2
        ctk.CTkLabel(form, text="Giá điện (VNĐ/kWh)").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_elec = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_elec.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.entry_elec.bind("<KeyRelease>", lambda e: format_money(self, e))

        ctk.CTkLabel(form, text="Giá nước (VNĐ/m³)").grid(row=2, column=1, sticky="w", padx=5, pady=5)
        self.entry_water = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_water.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.entry_water.bind("<KeyRelease>", lambda e: format_money(self, e))

        ctk.CTkLabel(form, text="Trạng thái").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.combo_status = ctk.CTkComboBox(
            form, 
            values=list(STATUS_MAP.keys()),
            height=36, 
            corner_radius=6,
            state="readonly"
        )
        self.combo_status.set("Trống")
        self.combo_status.grid(row=3, column=2, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(form, text="Ghi chú").grid(row=2, column=3, sticky="w", padx=5, pady=5)
        self.entry_note = ctk.CTkEntry(form, height=36, corner_radius=6)
        self.entry_note.grid(row=3, column=3, sticky="ew", padx=5, pady=5)

        # Separator between form and search
        ctk.CTkFrame(self, height=1, fg_color="#e0e0e0").pack(fill="x", padx=20, pady=(0, 10))

        # Search and filter section
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Tìm kiếm...",
            height=36,
            corner_radius=6
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.apply_search())
        
        # Search mode
        self.search_mode = ctk.CTkComboBox(
            search_frame,
            values=["Tên phòng", "Tầng", "Diện tích", "Giá thuê", "Tất cả"],
            height=36,
            corner_radius=6,
            state="readonly",
            width=150
        )
        self.search_mode.set("Tất cả")
        self.search_mode.pack(side="left", padx=(0, 10))
        
        # Status filter
        self.search_status = ctk.CTkComboBox(
            search_frame,
            values=["Tất cả"] + list(STATUS_MAP.keys()),
            height=36,
            corner_radius=6,
            state="readonly",
            width=120
        )
        self.search_status.set("Tất cả")
        self.search_status.pack(side="left", padx=(0, 10))
        
        # Search button
        self.btn_search = ctk.CTkButton(
            search_frame,
            text="Tìm kiếm",
            command=self.apply_search,
            height=36,
            corner_radius=6,
            width=120
        )
        self.btn_search.pack(side="left", padx=(0, 10))

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=50, pady=(0, 40))

        columns = ("id", "name", "floor", "area", "rent", "elec", "water", "status", "note")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=22)

        headers = ["ID", "Tên phòng", "Tầng", "Diện tích", "Giá thuê", "Giá điện", "Giá nước", "Trạng thái", "Ghi chú"]
        widths = [50, 150, 80, 100, 150, 120, 120, 120, 250]

        for col, text, w in zip(columns, headers, widths):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=w, anchor="center" if col not in ["name", "note"] else "w")

        # Style cho bảng
        style = ttk.Style()
        style.configure("Treeview", font=("Inter", 13), rowheight=40)
        style.configure("Treeview.Heading", font=("Inter", 13, "bold"))

        scroll = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scroll.pack(side="right", fill="y", padx=(0, 20), pady=20)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # format_money is imported from utils.format

    def _load_data(self):
        """Tải dữ liệu từ DB lên bảng"""
        self.rooms_cache = get_all_rooms()
        self.render_table(self.rooms_cache)

    def render_table(self, rooms):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for r in rooms:
            status_vn = STATUS_MAP_REV.get(r["status"], str(r["status"]))
            floor_val = r["floor"] if r["floor"] is not None else "-"
            area_val = r["area_m2"] if r["area_m2"] is not None else "-"

            self.tree.insert("", "end", values=(
                r["room_id"],
                r["room_name"],
                floor_val,
                area_val,
                format_currency(r["base_rent"]),
                format_currency(r["electric_unit_price"]),
                format_currency(r["water_unit_price"]),
                status_vn,
                r["note"] or ""
            ))

    def apply_search(self):
        query = (self.search_entry.get() or "").strip().lower()
        mode = self.search_mode.get()
        status_sel = self.search_status.get()
        status_db = None if status_sel == "Tất cả" else STATUS_MAP.get(status_sel)

        def match_room(r):
            if status_db and r["status"] != status_db:
                return False

            if not query:
                return True

            room_name = (r["room_name"] if r["room_name"] is not None else "").lower()
            if mode == "Tên phòng":
                return query in room_name

            floor = str(r["floor"]) if r["floor"] is not None else ""
            if mode == "Tầng":
                return query in floor

            floor = str(r["floor"]) if r["floor"] is not None else ""
            if mode == "Tầng":
                return query in floor

            if mode == "Diện tích":
                try:
                    input_area = float(query)  # người dùng nhập
                    area_m2 = r["area_m2"]
                    return area_m2 is not None and area_m2 <= input_area
                except ValueError:
                    return False

            if mode == "Gía thuê":
                try:
                    input_area = float(query)
                    base_rent = r["base_rent"]
                    return base_rent is not None and base_rent <= input_area
                except ValueError:
                    return False

            haystack = " ".join([
                str(r["room_name"] if r["room_name"] is not None else ""),
                str(r["floor"] if r["floor"] is not None else ""),
                str(r["area_m2"] if r["area_m2"] is not None else ""),
                str(r["base_rent"] if r["base_rent"] is not None else ""),
                str(r["electric_unit_price"] if r["electric_unit_price"] is not None else ""),
                str(r["water_unit_price"] if r["water_unit_price"] is not None else ""),
                str(r["status"] if r["status"] is not None else ""),
                str(STATUS_MAP_REV.get(r["status"], "") or ""),
                str(r["note"] if r["note"] is not None else ""),
            ]).lower()
            return query in haystack

        filtered = [r for r in self.rooms_cache if match_room(r)]
        self.render_table(filtered)

    # def clear_search(self):
    #     if hasattr(self, "search_entry"):
    #         self.search_entry.delete(0, "end")
    #     if hasattr(self, "search_mode"):
    #         self.search_mode.set("Tên phòng")
    #     if hasattr(self, "search_status"):
    #         self.search_status.set("Tất cả")
    #     self.render_table(self.rooms_cache)

    def _get_form_data(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên phòng!")
            self.entry_name.focus_set()
            return None
        try:
            # Validate area
            area_str = self.entry_area.get().strip()
            area = float(area_str) if area_str else 0.0
            if area < 0:
                messagebox.showwarning("Lỗi", "Diện tích phải là số dương!")
                self.entry_area.focus_set()
                return None

            floor_str = self.entry_floor.get().strip()
            floor = int(floor_str) if floor_str else None
            if floor is not None and floor < 0:
                messagebox.showwarning("Lỗi", "Số tầng phải là số dương!")
                self.entry_floor.focus_set()
                return None

            def validate_money(value, field_name, default):
                try:
                    val = parse_currency(value or str(default))
                    if val < 0:
                        messagebox.showwarning("Lỗi", f"{field_name} không được âm!")
                        return None
                    return val
                except ValueError:
                    messagebox.showwarning("Lỗi", f"Giá trị {field_name} không hợp lệ!")
                    return None

            rent = validate_money(self.entry_rent.get(), "Giá thuê", 0)
            elec = validate_money(self.entry_elec.get(), "Giá điện", 3500)
            water = validate_money(self.entry_water.get(), "Giá nước", 10000)

            if None in (rent, elec, water):
                return None

        except ValueError as e:
            messagebox.showerror("Lỗi",
                                 f"Dữ liệu nhập vào không hợp lệ!\n{str(e)}")
            return None

        return {
            "room_name": name,
            "area_m2": area,
            "floor": floor,
            "base_rent": rent,
            "electric_unit_price": elec,
            "water_unit_price": water,
            "status": STATUS_MAP[self.combo_status.get()],
            "note": self.entry_note.get().strip() or None
        }

    def reset_form(self):
        self.current_room_id = None
        for e in (self.entry_name, self.entry_area, self.entry_floor,
                  self.entry_rent, self.entry_elec, self.entry_water, self.entry_note):
            e.delete(0, "end")

        self.combo_status.set("Trống")

        self.btn_add.configure(state="normal")
        self.btn_update.configure(state="disabled")
        self.btn_delete.configure(state="disabled")

        # Bỏ chọn trên bảng
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return

        # Lấy dữ liệu dòng được chọn
        v = self.tree.item(sel[0])["values"]
        self.current_room_id = v[0]  # ID phòng

        # Fill dữ liệu lên form
        self.entry_name.delete(0, "end");
        self.entry_name.insert(0, v[1])

        self.entry_floor.delete(0, "end")
        if v[2] != "-": self.entry_floor.insert(0, v[2])

        self.entry_area.delete(0, "end")
        if v[3] != "-": self.entry_area.insert(0, v[3])

        self.entry_rent.delete(0, "end");
        self.entry_rent.insert(0, v[4])
        self.entry_elec.delete(0, "end");
        self.entry_elec.insert(0, v[5])
        self.entry_water.delete(0, "end");
        self.entry_water.insert(0, v[6])

        self.combo_status.set(v[7])

        self.entry_note.delete(0, "end")
        self.entry_note.insert(0, v[8])

        self.btn_add.configure(state="disabled")
        self.btn_update.configure(state="normal")
        self.btn_delete.configure(state="normal")

    def add_room(self):
        data = self._get_form_data()
        if not data: return

        if any(r["room_name"].upper() == data["room_name"].upper() for r in self.rooms_cache):
            messagebox.showwarning("Lỗi", f"Phòng '{data['room_name']}' đã tồn tại!")
            return
        try:
            create_room(data)
            messagebox.showinfo("Thành công", "Thêm phòng mới thành công!")
            self._load_data()
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Không thể thêm phòng:\n{str(e)}")

    def update_room(self):
        if not self.current_room_id: return

        data = self._get_form_data()
        if not data: return

        # Check trùng tên (trừ chính phòng đang sửa)
        for r in self.rooms_cache:
            if (r["room_name"].upper() == data["room_name"].upper() and
                    str(r["room_id"]) != str(self.current_room_id)):
                messagebox.showwarning("Lỗi", "Tên phòng này đã tồn tại!")
                return
        try:
            update_room(self.current_room_id, data)
            messagebox.showinfo("Thành công", "Cập nhật thông tin phòng thành công!")
            self._load_data()
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Cập nhật thất bại:\n{str(e)}")

    def delete_room(self):
        if not self.current_room_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn phòng cần xóa!")
            return

        # Lấy tên phòng để hiển thị trong thông báo xác nhận
        room_name = ""
        for room in self.rooms_cache:
            if room["room_id"] == self.current_room_id:
                room_name = room["room_name"]
                break
        confirm = messagebox.askyesno(
            "Xác nhận",
            f"Bạn có chắc chắn muốn xóa phòng {room_name}?\n")

        if not confirm:
            return
        try:
            delete_room(self.current_room_id)
            messagebox.showinfo(
                "Thành công",
                f"Đã xóa phòng {room_name} thành công!"
            )
            self._load_data()
            self.reset_form()
        except ValueError as e:
            # Lỗi từ service (ví dụ: phòng đang có hợp đồng active)
            messagebox.showerror("Không thể xóa", str(e))
        except Exception as e:
            # Lỗi hệ thống không mong muốn
            messagebox.showerror(
                "Lỗi",
                f"Đã xảy ra lỗi khi xóa phòng.\nLỗi: {str(e)}"
            )
