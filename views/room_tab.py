import customtkinter as ctk
from tkinter import ttk, messagebox
from services.room_service import get_all_rooms, create_room, update_room, delete_room
from utils.format import parse_currency, format_currency, parse_currency

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
        self.search_mode = None
        self.current_room_id = None

        # Biến cache để lưu danh sách phòng (giúp check trùng tên nhanh hơn)
        self.rooms_cache = []

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # Main form
        self._build_form()
        # Table
        self._build_table()

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=(12, 6))

        # Row 0: Room Info
        ctk.CTkLabel(form, text="Tên phòng *").grid(row=0, column=0, sticky="w")
        self.entry_name = ctk.CTkEntry(form, width=160)
        self.entry_name.grid(row=0, column=1, padx=6, sticky="w")

        ctk.CTkLabel(form, text="Tầng").grid(row=0, column=2, sticky="w")
        self.entry_floor = ctk.CTkEntry(form, width=100)
        self.entry_floor.grid(row=0, column=3, padx=6, sticky="w")

        # Row 1: Room Details
        ctk.CTkLabel(form, text="Diện tích (m²)").grid(row=1, column=0, sticky="w")
        self.entry_area = ctk.CTkEntry(form, width=160)
        self.entry_area.grid(row=1, column=1, padx=6, sticky="w")

        ctk.CTkLabel(form, text="Trạng thái").grid(row=1, column=2, sticky="w")
        self.combo_status = ctk.CTkComboBox(
            form,
            values=list(STATUS_MAP.keys()),
            width=100,
            state="readonly"
        )
        self.combo_status.set("Trống")
        self.combo_status.grid(row=1, column=3, padx=6, sticky="w")

        # Row 2: Pricing
        ctk.CTkLabel(form, text="Giá thuê").grid(row=2, column=0, sticky="w")
        self.entry_rent = ctk.CTkEntry(form, width=160)
        self.entry_rent.grid(row=2, column=1, padx=6, sticky="w")
        self.entry_rent.bind("<KeyRelease>", lambda e: parse_currency(self, e))

        ctk.CTkLabel(form, text="Giá điện").grid(row=2, column=2, sticky="w")
        self.entry_elec = ctk.CTkEntry(form, width=100)
        self.entry_elec.grid(row=2, column=3, padx=6, sticky="w")
        self.entry_elec.bind("<KeyRelease>", lambda e: parse_currency(self, e))

        # Row 3: More Pricing
        ctk.CTkLabel(form, text="Giá nước").grid(row=3, column=0, sticky="w")
        self.entry_water = ctk.CTkEntry(form, width=160)
        self.entry_water.grid(row=3, column=1, padx=6, sticky="w")
        self.entry_water.bind("<KeyRelease>", lambda e: parse_currency(self, e))

        ctk.CTkLabel(form, text="Ghi chú").grid(row=3, column=2, sticky="w")
        self.entry_note = ctk.CTkEntry(form, width=300)
        self.entry_note.grid(row=3, column=3, padx=6, sticky="we")

        # Action buttons and search
        action = ctk.CTkFrame(form, fg_color="transparent")
        action.grid(row=4, column=0, columnspan=8, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(action, text="Tìm kiếm").pack(side="left")
        self.search_entry = ctk.CTkEntry(action, width=200)
        self.search_entry.pack(side="left", padx=6)
        self.search_entry.bind("<Return>", lambda e: self.apply_search())

        self.search_status = ctk.CTkComboBox(
            action,
            values=["Tất cả"] + list(STATUS_MAP.keys()),
            width=120,
            state="readonly"
        )
        self.search_status.set("Tất cả")
        self.search_status.pack(side="left", padx=6)

        ctk.CTkButton(action, text="Tìm", width=60, command=self.apply_search).pack(side="left")

        ctk.CTkButton(action, text="Xóa", fg_color="#e74c3c", command=self.delete_room).pack(side="right", padx=6)
        ctk.CTkButton(action, text="Cập nhật", fg_color="#f39c12", command=self.update_room).pack(side="right", padx=6)
        ctk.CTkButton(action, text="Thêm mới", fg_color="#27ae60", command=self.add_room).pack(side="right", padx=6)
        ctk.CTkButton(action, text="Làm mới", fg_color="#7f8c8d", command=self.reset_form).pack(side="right", padx=6)

    def _build_table(self, columns=None):
        # Treeview frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Define columns and headers
        cols = ("id", "name", "floor", "area", "rent", "elec", "water", "status", "note")
        headers = {
            "id": "ID",
            "name": "Tên phòng",
            "floor": "Tầng",
            "area": "Diện tích",
            "rent": "Giá thuê",
            "elec": "Giá điện",
            "water": "Giá nước",
            "status": "Trạng thái",
            "note": "Ghi chú"
        }

        # Configure column widths and anchors
        widths = {
            "id": 40,
            "name": 120,
            "floor": 60,
            "area": 80,
            "rent": 100,
            "elec": 100,
            "water": 100,
            "status": 100,
            "note": 200
        }
        anchors = {
            "id": "center",
            "name": "w",
            "floor": "center",
            "area": "center",
            "rent": "e",
            "elec": "e",
            "water": "e",
            "status": "center",
            "note": "w"
        }

        # Create and configure treeview
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        # Set up columns and headers
        for col in cols:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor=anchors[col])

        # Add scrollbar
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        # Pack treeview and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_select_room)

        # Style cho bảng
        style = ttk.Style()
        style.configure("Treeview", font=("Inter", 13), rowheight=40)
        style.configure("Treeview.Heading", font=("Inter", 13, "bold"))

    def on_select_room(self, event):
        """Handle row selection in the room table"""
        selected = self.tree.selection()
        if not selected:
            return

        # Get the selected item
        item = self.tree.item(selected[0])
        values = item['values']

        if not values:
            return

        # Update form fields with selected room data
        self.current_room_id = values[0]  # ID
        self.entry_name.delete(0, 'end')
        self.entry_name.insert(0, values[1])  # Name
        self.entry_floor.delete(0, 'end')
        self.entry_floor.insert(0, values[2])  # Floor
        self.entry_area.delete(0, 'end')
        self.entry_area.insert(0, values[3])  # Area
        self.entry_rent.delete(0, 'end')
        self.entry_rent.insert(0, values[4])  # Rent
        self.entry_elec.delete(0, 'end')
        self.entry_elec.insert(0, values[5])  # Electricity price
        self.entry_water.delete(0, 'end')
        self.entry_water.insert(0, values[6])  # Water price

        # Set status
        status_text = values[7]  # Status text
        for key, value in STATUS_MAP.items():
            if key == status_text:
                self.combo_status.set(key)
                break

        self.entry_note.delete(0, 'end')
        if len(values) > 8:  # Note is optional
            self.entry_note.insert(0, values[8])

        # Buttons are already managed in the action bar, no need to enable/disable here

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

        # Buttons are managed in the action bar, no need to enable/disable them here
        # as they are always visible in the new layout

        # Clear selection in the table
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

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