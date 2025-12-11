import customtkinter as ctk
from tkinter import ttk, messagebox
from services.room_service import get_all_rooms, create_room, update_room, delete_room
# from utils.formatter import format_currency, parse_currency

# Định nghĩa hằng số trạng thái để đồng bộ giữa Tiếng Việt (UI) và Tiếng Anh (Database)
STATUS_MAP = {
    "Trống": "available",
    "Đang thuê": "occupied",
    "Bảo trì": "maintenance"
}
# Map ngược để hiển thị lên bảng: {"available": "Trống", ...}
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
        # --- TIÊU ĐỀ ---
        ctk.CTkLabel(
            self,
            text="QUẢN LÝ PHÒNG TRỌ",
            font=("Inter", 28, "bold"),
            text_color="#0041DE",
        ).pack(pady=(30, 20))

        # --- FORM NHẬP LIỆU ---
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=20)
        form_frame.pack(fill="x", padx=50, pady=(0, 25))

        form = ctk.CTkFrame(form_frame, fg_color="transparent")
        form.pack(fill="x", padx=60, pady=35)
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # -- Hàng 1 --
        # Tên phòng
        ctk.CTkLabel(form, text="Tên phòng *", font=("Inter", 14, "bold")).grid(row=0, column=0, sticky="w",
                                                                                pady=(0, 5))
        self.entry_name = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: P101")
        self.entry_name.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # Số tầng
        ctk.CTkLabel(form, text="Số tầng", font=("Inter", 14, "bold")).grid(row=0, column=1, sticky="w", pady=(0, 5),
                                                                            padx=(30, 0))
        self.entry_floor = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15), placeholder_text="VD: 1")
        self.entry_floor.grid(row=1, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))

        # Diện tích
        ctk.CTkLabel(form, text="Diện tích (m²)", font=("Inter", 14, "bold")).grid(row=0, column=2, sticky="w",
                                                                                   pady=(0, 5), padx=(30, 0))
        self.entry_area = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: 25.5")
        self.entry_area.grid(row=1, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        # Giá thuê
        ctk.CTkLabel(form, text="Giá thuê (VNĐ)", font=("Inter", 14, "bold")).grid(row=0, column=3, sticky="w",
                                                                                   pady=(0, 5), padx=(30, 0))
        self.entry_rent = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="VD: 2.500.000")
        self.entry_rent.grid(row=1, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_rent.bind("<KeyRelease>", self._format_money)

        # -- Hàng 2 --
        # Giá điện
        ctk.CTkLabel(form, text="Giá điện (VNĐ/kWh)", font=("Inter", 14, "bold")).grid(row=2, column=0, sticky="w",
                                                                                       pady=(0, 5))
        self.entry_elec = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                       placeholder_text="Mặc định: 3.500")
        self.entry_elec.grid(row=3, column=0, sticky="ew", pady=(0, 20))
        self.entry_elec.bind("<KeyRelease>", self._format_money)

        # Giá nước
        ctk.CTkLabel(form, text="Giá nước (VNĐ/m³)", font=("Inter", 14, "bold")).grid(row=2, column=1, sticky="w",
                                                                                      pady=(0, 5), padx=(30, 0))
        self.entry_water = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15),
                                        placeholder_text="Mặc định: 10.000")
        self.entry_water.grid(row=3, column=1, sticky="ew", pady=(0, 20), padx=(30, 0))
        self.entry_water.bind("<KeyRelease>", self._format_money)

        # Trạng thái
        ctk.CTkLabel(form, text="Trạng thái", font=("Inter", 14, "bold")).grid(row=2, column=2, sticky="w", pady=(0, 5),
                                                                               padx=(30, 0))
        self.combo_status = ctk.CTkComboBox(form, values=list(STATUS_MAP.keys()), height=40, corner_radius=7,
                                            font=("Inter", 15), state="readonly")
        self.combo_status.set("Trống")
        self.combo_status.grid(row=3, column=2, sticky="ew", pady=(0, 20), padx=(30, 0))

        # Ghi chú
        ctk.CTkLabel(form, text="Ghi chú", font=("Inter", 14, "bold")).grid(row=2, column=3, sticky="w", pady=(0, 5),
                                                                            padx=(30, 0))
        self.entry_note = ctk.CTkEntry(form, height=40, corner_radius=7, font=("Inter", 15))
        self.entry_note.grid(row=3, column=3, sticky="ew", pady=(0, 20), padx=(30, 0))

        # --- BUTTONS ---
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

        self.btn_delete = ctk.CTkButton(btn_right, text="Xóa Phòng", height=44, corner_radius=7,
                                        font=("Inter", 15, "bold"), fg_color="#F50002", hover_color="#C91D1D",
                                        command=self.delete_room)

        self.btn_reset = ctk.CTkButton(btn_right, text="Làm Mới", height=44, corner_radius=7,
                                       font=("Inter", 15, "bold"), fg_color="#282D33", hover_color="#1F2327",
                                       command=self.reset_form)
        self.btn_reset.pack(side="right", padx=8)

        # --- TABLE (Treeview) ---
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
        val = w.get().replace(".", "")
        if val.isdigit():
            w.delete(0, "end")
            w.insert(0, format_currency(int(val)))

    def _load_data(self):
        """Tải dữ liệu từ DB lên bảng"""
        # Xóa dữ liệu cũ trên bảng
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Lấy dữ liệu mới từ BE (Giả sử BE đã sửa câu SELECT có trả về room_id và name_room)
        self.rooms_cache = get_all_rooms()

        for r in self.rooms_cache:
            # Chuyển đổi trạng thái từ Anh sang Việt
            status_vn = STATUS_MAP_REV.get(r["status"], r["status"])

            # Xử lý các trường có thể bị None từ DB
            floor_val = r["floor"] if r["floor"] is not None else "-"
            area_val = r["area_m2"] if r["area_m2"] is not None else "-"

            self.tree.insert("", "end", values=(
                r["room_id"],  # Cần BE trả về room_id
                r["name_room"],  # Cần BE trả về name_room
                floor_val,
                area_val,
                format_currency(r["base_rent"]),
                format_currency(r["electric_unit_price"]),
                format_currency(r["water_unit_price"]),
                status_vn,
                r["note"] or ""
            ))

    def _get_form_data(self):
        """Hàm lấy dữ liệu từ form và kiểm tra lỗi nhập liệu"""
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên phòng!")
            return None

        try:
            # Xử lý diện tích và tầng (nếu để trống thì là None hoặc 0)
            area_str = self.entry_area.get().strip()
            area = float(area_str) if area_str else 0.0

            floor_str = self.entry_floor.get().strip()
            floor = int(floor_str) if floor_str else None

            # Xử lý tiền tệ (Parse từ chuỗi "2.500.000" -> số int)
            # Nếu để trống thì lấy giá trị mặc định
            rent = parse_currency(self.entry_rent.get() or "0")
            elec = parse_currency(self.entry_elec.get() or "3500")
            water = parse_currency(self.entry_water.get() or "10000")

        except ValueError:
            messagebox.showerror("Lỗi nhập liệu",
                                 "Diện tích và Số tầng phải là số hợp lệ!\nVí dụ: 25.5 (Diện tích), 1 (Tầng)")
            return None

        return {
            "name_room": name,
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

        # Reset nút bấm
        self.btn_add.pack(side="right", padx=8)
        self.btn_update.pack_forget()
        self.btn_delete.pack_forget()

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

        # Đổi nút bấm
        self.btn_add.pack_forget()
        self.btn_update.pack(side="right", padx=8)
        self.btn_delete.pack(side="right", padx=8)

    def add_room(self):
        data = self._get_form_data()
        if not data: return

        # Check trùng tên (dùng danh sách cache)
        if any(r["name_room"].upper() == data["name_room"].upper() for r in self.rooms_cache):
            messagebox.showwarning("Trùng lặp", f"Phòng '{data['name_room']}' đã tồn tại!")
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
            if (r["name_room"].upper() == data["name_room"].upper() and
                    str(r["room_id"]) != str(self.current_room_id)):
                messagebox.showwarning("Trùng lặp", "Tên phòng này đang được sử dụng bởi phòng khác!")
                return

        try:
            update_room(self.current_room_id, data)
            messagebox.showinfo("Thành công", "Cập nhật thông tin phòng thành công!")
            self._load_data()
            self.reset_form()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", f"Cập nhật thất bại:\n{str(e)}")

    def delete_room(self):
        if not self.current_room_id: return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa phòng này không?"):
            try:
                delete_room(self.current_room_id)
                messagebox.showinfo("Thành công", "Đã xóa phòng!")
                self._load_data()
                self.reset_form()
            except Exception as e:
                # Lỗi này thường do BE ném ra (khi phòng đang có hợp đồng active)
                messagebox.showerror("Không thể xóa", str(e))