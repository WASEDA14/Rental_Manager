import customtkinter as ctk
from tkinter import ttk, messagebox
from services.room_service import get_all_rooms, create_room, update_room, delete_room
from views.bill_tab import format_currency

from utils.format import parse_currency

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
        # self.user_id = None
        self.current_room_id = None

        # Biến cache để lưu danh sách phòng (giúp check trùng tên nhanh hơn)
        self.rooms_cache = []

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        ctk.CTkLabel(
            self,
            text="QUẢN LÝ PHÒNG TRỌ",
            font=("Inter", 28, "bold"),
            text_color="#0041DE",
        ).pack(pady=(30, 20))

        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        form_frame.pack(fill="x", padx=50, pady=(0, 25))

        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=60, pady=35)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(form, text="Tên phòng *", font=("Inter", 14, "bold")).grid(row=0, column=0, sticky="w",
                                                                                pady=(0, 5))
        self.entry_name = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_name.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        ctk.CTkLabel(form, text="Số tầng", font=("Inter", 14, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5),
                                                                            padx=(30, 0))
        self.entry_floor = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_floor.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Diện tích (m²)", font=("Inter", 14, "bold")).grid(row=0, column=2, sticky="w",
                                                                                   pady=(0, 5), padx=(30, 0))
        self.entry_area = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_area.grid(row=1, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Giá thuê (VNĐ)", font=("Inter", 14, "bold")).grid(row=0, column=3, sticky="w",
                                                                                   pady=(0, 5), padx=(30, 0))
        self.entry_rent = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_rent.grid(row=1, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_rent.bind("<KeyRelease>", self._format_money)

        ctk.CTkLabel(form, text="Giá điện (VNĐ/kWh)", font=("Inter", 14, "bold")).grid(row=2, column=0, sticky="w",
                                                                                       pady=(0, 5))
        self.entry_elec = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_elec.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        self.entry_elec.bind("<KeyRelease>", self._format_money)

        ctk.CTkLabel(form, text="Giá nước (VNĐ/m³)", font=("Inter", 14, "bold")).grid(row=2, column=1, sticky="w",
                                                                                      pady=(0, 5), padx=(30, 0))
        self.entry_water = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_water.grid(row=3, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_water.bind("<KeyRelease>", self._format_money)

        ctk.CTkLabel(form, text="Trạng thái", font=("Inter", 14, "bold")).grid(row=2, column=2, sticky="w", pady=(0, 5),
                                                                               padx=(30, 0))
        self.combo_status = ctk.CTkComboBox(form, values=list(STATUS_MAP.keys()), height=40, corner_radius=7,
                                            font=("Inter", 15), state="readonly")
        self.combo_status.set("Trống")
        self.combo_status.grid(row=3, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        ctk.CTkLabel(form, text="Ghi chú", font=("Inter", 14, "bold")).grid(row=2, column=3, sticky="w", pady=(0, 5),
                                                                            padx=(30, 0))
        self.entry_note = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_note.grid(row=3, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))

        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=60, pady=(10, 30))
        btn_right = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_right.pack(side="right")

        self.btn_add = ctk.CTkButton(btn_right, text="Thêm Phòng", height=44, corner_radius=7,
                                     font=("Inter", 15, "bold"), fg_color="#00B63E", hover_color="#02A037",
                                     command=self.add_room)
        self.btn_add.pack(side="right", padx=8)

        self.btn_update = ctk.CTkButton(btn_right, text="Cập Nhật", height=44, corner_radius=7,
                                        font=("Inter", 15, "bold"), fg_color="#0067F7", hover_color="#225CD8",
                                        command=self.update_room)

        self.btn_update.configure(state="disabled")
        self.btn_update.pack(side="right", padx=8)

        self.btn_delete = ctk.CTkButton(btn_right, text="Xóa Phòng", height=44, corner_radius=7,
                                        font=("Inter", 15, "bold"), fg_color="#F50002", hover_color="#C91D1D",
                                        command=self.delete_room)

        self.btn_delete.configure(state="disabled")
        self.btn_delete.pack(side="right", padx=8)

        self.btn_reset = ctk.CTkButton(btn_right, text="Làm Mới", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#282D33", hover_color="#1F2327",
                                       command=self.reset_form)
        self.btn_reset.pack(side="right", padx=8)

        search_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=12)
        search_frame.pack(fill="x", padx=50, pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(search_frame, height=38, corner_radius=7,
                                         font=("Inter", 14))
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=12)

        self.search_mode = ctk.CTkComboBox(
            search_frame,
            values=["Tên phòng", "Tầng", "Diện tích", "Gía thuê", "Tất cả"],
            height=38,
            corner_radius=7,
            font=("Inter", 14),
            state="readonly",
            width=170,
        )
        self.search_mode.set("Tên phòng")
        self.search_mode.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=12)

        self.search_status = ctk.CTkComboBox(
            search_frame,
            values=["Tất cả"] + list(STATUS_MAP.keys()),
            height=38,
            corner_radius=7,
            font=("Inter", 14),
            state="readonly",
            width=140,
        )
        self.search_status.set("Tất cả")
        self.search_status.grid(row=0, column=2, sticky="e", padx=(0, 10), pady=12)

        self.btn_search = ctk.CTkButton(
            search_frame,
            text="Tìm",
            height=38,
            corner_radius=7,
            font=("Inter", 14, "bold"),
            fg_color="#0067F7",
            hover_color="#225CD8",
            command=self.apply_search,
            width=80,
        )
        self.btn_search.grid(row=0, column=3, sticky="e", padx=(0, 10), pady=12)

        self.btn_clear_search = ctk.CTkButton(
            search_frame,
            text="Xóa",
            height=38,
            corner_radius=7,
            font=("Inter", 14, "bold"),
            fg_color="#282D33",
            hover_color="#1F2327",
            command=self.clear_search,
            width=80,
        )
        self.btn_clear_search.grid(row=0, column=4, sticky="e", padx=(0, 20), pady=12)

        self.search_entry.bind("<Return>", lambda _e: self.apply_search())

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

    def _format_money(self, event):
        """Format số tiền có dấu chấm phân cách khi nhập"""
        w = event.widget
        current = w.get()

        # Allow backspace and delete
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End'):
            return

        # Allow only digits and control characters
        if event.char and not event.char.isdigit() and event.char not in ('\b', '\t'):
            return 'break'

        # Get current cursor position
        cursor_pos = w.index('insert')

        # Format the number
        try:
            # Get the raw value (remove all non-digit characters)
            raw = ''.join(c for c in current if c.isdigit())
            if not raw:  # If empty, allow it
                return

            # Format the number with thousand separators
            num = int(raw)
            formatted = format_currency(num)

            # Update the entry
            w.delete(0, 'end')
            w.insert(0, formatted)

            # Set cursor position
            w.icursor(cursor_pos + (len(formatted) - len(current)))
        except ValueError:
            # If conversion fails, revert to empty
            w.delete(0, 'end')

        return 'break'

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

    def clear_search(self):
        if hasattr(self, "search_entry"):
            self.search_entry.delete(0, "end")
        if hasattr(self, "search_mode"):
            self.search_mode.set("Tên phòng")
        if hasattr(self, "search_status"):
            self.search_status.set("Tất cả")
        self.render_table(self.rooms_cache)

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
