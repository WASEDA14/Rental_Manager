# views/contract_tab.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os
from services.contract_service import (
    get_all_contracts,
    create_contract,
    update_contract,
    delete_contract,
    end_contract,
    get_available_rooms,
    get_tenants_without_active_contract, 
    get_contract_by_id,
    export_contract_to_pdf
)


# Helper format tiền tệ
def format_currency(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


class contractView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._selected_id = None

        # Cache dữ liệu cho Combobox (ID -> Data)
        self.rooms_map = {}
        self.tenants_map = {}

        # ===== Variables =====
        self.room_var = ctk.StringVar()
        self.tenant_var = ctk.StringVar()
        self.contact_name_var = ctk.StringVar()
        self.rent_var = ctk.StringVar()
        self.deposit_var = ctk.StringVar()
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        self.deposit_date_var = ctk.StringVar()

        self.elec_start_var = ctk.StringVar(value="0")
        self.water_start_var = ctk.StringVar(value="0")
        self.note_var = ctk.StringVar()
        self.search_var = ctk.StringVar()

        # ===== UI Layout =====
        self._build_form()
        self._build_table()
        self._build_actions()

        # Load Data
        self._load_combobox_data()
        self.reload()

    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=(12, 6))

        # --- Row 0 ---
        ctk.CTkLabel(form, text="Phòng *").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.cb_room = ctk.CTkComboBox(form, width=160, variable=self.room_var, command=self.on_room_select)
        self.cb_room.grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="Khách Thuê *").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        self.cb_tenant = ctk.CTkComboBox(form, width=160, variable=self.tenant_var, command=self.on_tenant_select)
        self.cb_tenant.grid(row=0, column=3, padx=6, pady=6)

        ctk.CTkLabel(form, text="Người Liên Hệ").grid(row=0, column=4, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.contact_name_var, width=160).grid(row=0, column=5, padx=6, pady=6)

        # --- Row 1 ---
        ctk.CTkLabel(form, text="Giá Thuê (VND)").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.rent_var, width=160).grid(row=1, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="Tiền Cọc (VND)").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.deposit_var, width=160).grid(row=1, column=3, padx=6, pady=6)

        ctk.CTkLabel(form, text="Ngày Cọc").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        DateEntry(form, textvariable=self.deposit_date_var, width=16, date_pattern="yyyy-mm-dd").grid(row=1, column=5,
                                                                                                      padx=6, pady=6,
                                                                                                      sticky="w")

        # --- Row 2 ---
        ctk.CTkLabel(form, text="Ngày Bắt Đầu").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        DateEntry(form, textvariable=self.start_date_var, width=16, date_pattern="yyyy-mm-dd").grid(row=2, column=1,
                                                                                                    padx=6, pady=6,
                                                                                                    sticky="w")

        ctk.CTkLabel(form, text="Ngày Kết Thúc").grid(row=2, column=2, padx=6, pady=6, sticky="w")
        DateEntry(form, textvariable=self.end_date_var, width=16, date_pattern="yyyy-mm-dd").grid(row=2, column=3,
                                                                                                  padx=6, pady=6,
                                                                                                  sticky="w")

        # --- Row 3 ---
        ctk.CTkLabel(form, text="Điện Đầu (kWh)").grid(row=3, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.elec_start_var, width=160).grid(row=3, column=1, padx=6, pady=6)

        ctk.CTkLabel(form, text="Nước Đầu (m³)").grid(row=3, column=2, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.water_start_var, width=160).grid(row=3, column=3, padx=6, pady=6)

        # --- Row 4 ---
        ctk.CTkLabel(form, text="Ghi Chú").grid(row=4, column=0, padx=6, pady=6, sticky="w")
        ctk.CTkEntry(form, textvariable=self.note_var, width=450).grid(row=4, column=1, columnspan=5, padx=6, pady=6,
                                                                       sticky="we")

    def _build_table(self):
        # Search & Actions Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=12, pady=(6, 0))

        ctk.CTkEntry(toolbar, textvariable=self.search_var, placeholder_text="Tìm kiếm...", width=200).pack(side="left")
        ctk.CTkButton(toolbar, text="Tìm", command=self.reload, width=60).pack(side="left", padx=6)
        ctk.CTkButton(toolbar, text="Tải lại", command=self._full_reload, width=60, fg_color="gray").pack(side="left",
                                                                                                          padx=6)

        ctk.CTkButton(toolbar, text="Xuất hợp đồng", command=self.on_export_pdf, fg_color="#3498db").pack(side="right", padx=6)
        ctk.CTkButton(toolbar, text="Tạo Mới", command=self.on_create, fg_color="#27ae60").pack(side="right", padx=6)
        ctk.CTkButton(toolbar, text="Cập Nhật", command=self.on_update, fg_color="#f39c12").pack(side="right", padx=6)
        ctk.CTkButton(toolbar, text="Xóa", command=self.on_delete, fg_color="#e74c3c").pack(side="right", padx=6)
        ctk.CTkButton(toolbar, text="Kết Thúc HĐ", command=self.on_end_contract, fg_color="#8e44ad").pack(side="right",
                                                                                                          padx=6)

        # Treeview
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=12, pady=6)

        cols = ("id", "room", "tenant", "start", "end", "rent", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=14)

        self.tree.heading("id", text="ID")
        self.tree.heading("room", text="Phòng")
        self.tree.heading("tenant", text="Khách Thuê")
        self.tree.heading("start", text="Bắt Đầu")
        self.tree.heading("end", text="Kết Thúc")
        self.tree.heading("rent", text="Giá Thuê")
        self.tree.heading("status", text="Trạng Thái")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("room", width=80, anchor="center")
        self.tree.column("tenant", width=150)
        self.tree.column("start", width=100, anchor="center")
        self.tree.column("end", width=100, anchor="center")
        self.tree.column("rent", width=100, anchor="e")
        self.tree.column("status", width=100, anchor="center")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

    def _build_actions(self):
        # Nút Clear ở dưới cùng (hoặc gộp vào toolbar)
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(bottom, text="Làm Mới Form", command=self.on_clear, fg_color="#34495e").pack(side="right")

    # ===== Logic Load Data =====

    def _load_combobox_data(self):
        # 1. Load Available Rooms
        rooms = get_available_rooms()  # [(id, name, rent), ...]
        self.rooms_map = {r[1]: {"id": r[0], "rent": r[2]} for r in rooms}
        self.cb_room.configure(values=list(self.rooms_map.keys()))

        # 2. Load Tenants without Contract
        tenants = get_tenants_without_active_contract()  # [(id, name), ...]
        self.tenants_map = {t[1]: t[0] for t in tenants}
        self.cb_tenant.configure(values=list(self.tenants_map.keys()))

    def reload(self):
        rows = get_all_contracts()
        kw = self.search_var.get().lower().strip()

        self.tree.delete(*self.tree.get_children())

        for r in rows:
            # r index: 0:id, ..., -2: room_name, -1: tenant_name (check lại BE SQL)
            # BE: SELECT c.*, r.room_name, t.full_name
            # c.* giả sử có 14 cột. r.room_name là cột kế cuối, t.full_name là cột cuối.

            # Để an toàn, truy cập bằng index âm hoặc key nếu trả về dict-like row
            c_id = r[0]
            room_name = r['room_name']  # Nếu dùng sqlite3.Row
            tenant_name = r['full_name']
            start_date = r['start_ymd']
            end_date = r['end_ymd']
            rent = r['rent']
            status = r['contract_status']

            if kw and (kw not in str(c_id) and kw not in room_name.lower() and kw not in tenant_name.lower()):
                continue

            self.tree.insert("", "end", values=(
                c_id, room_name, tenant_name, start_date, end_date,
                format_currency(rent), status.capitalize()
            ))

    def _full_reload(self):
        """Reload cả bảng và combobox"""
        self._load_combobox_data()
        self.reload()
        self.on_clear()

    # ===== Event Handlers =====

    def on_room_select(self, choice):
        # Tự động điền giá thuê khi chọn phòng
        if choice in self.rooms_map:
            rent = self.rooms_map[choice]["rent"]
            self.rent_var.set(str(int(rent)))

    def on_tenant_select(self, choice):
        # Tự động điền người liên hệ là tên khách thuê
        self.contact_name_var.set(choice)

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel: return

        # Lấy ID từ dòng chọn
        item = self.tree.item(sel[0])
        self._selected_id = int(item["values"][0])

        # Load chi tiết để fill form (vì bảng thiếu thông tin như điện/nước/cọc)
        # Cách tốt nhất là gọi get_contract_by_id từ BE, nhưng BE trả về tuple c.* chưa join
        # Ở đây ta dùng data từ bảng kết hợp tìm trong list get_all_contracts hoặc query lại

        # Query lại cho chắc chắn
        # Note: get_all_contracts trả về list, ta lọc ra
        all_contracts = get_all_contracts()
        contract = next((c for c in all_contracts if c[0] == self._selected_id), None)

        if contract:
            # Mapping dữ liệu (cần khớp thứ tự cột trong DB table 'contract')
            # 0:id, 1:room_id, 2:tenant_id, 3:contract_name, 4:start, 5:end,
            # 6:rent, 7:deposit, 8:elec_start, 9:water_start, 10:deposit_date, 11:status, 12:note, 13:deleted
            # + room_name, full_name

            self.room_var.set(contract['room_name'])
            self.tenant_var.set(contract['full_name'])
            self.contact_name_var.set(contract['contract_name'])
            self.rent_var.set(str(int(contract['rent'])))
            self.deposit_var.set(str(int(contract['deposit_amount'])))
            self.start_date_var.set(contract['start_ymd'])
            self.end_date_var.set(contract['end_ymd'])
            self.deposit_date_var.set(contract['deposit_ymd'])
            self.elec_start_var.set(str(contract['electric_meter_start']))
            self.water_start_var.set(str(contract['water_meter_start']))
            self.note_var.set(contract['note'] or "")

            # Disable combobox khi edit để tránh lỗi logic đổi phòng/khách
            self.cb_room.configure(state="disabled")
            self.cb_tenant.configure(state="disabled")

    def on_clear(self):
        self._selected_id = None
        self.room_var.set("")
        self.tenant_var.set("")
        self.contact_name_var.set("")
        self.rent_var.set("")
        self.deposit_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        self.deposit_date_var.set("")
        self.elec_start_var.set("0")
        self.water_start_var.set("0")
        self.note_var.set("")

        # Re-enable combobox
        self.cb_room.configure(state="normal")
        self.cb_tenant.configure(state="normal")

        # Bỏ chọn bảng
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    # ===== CRUD Actions =====

    def _get_form_data(self):
        # Validate cơ bản
        if not self.room_var.get() or not self.tenant_var.get():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Phòng và Khách thuê!")
            return None

        try:
            rent = int(self.rent_var.get().replace(".", "").replace(",", ""))
            deposit = int(self.deposit_var.get().replace(".", "").replace(",", "") or 0)
            elec = int(self.elec_start_var.get() or 0)
            water = int(self.water_start_var.get() or 0)
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Giá tiền, Điện, Nước phải là số!")
            return None

        # Lấy ID từ tên hiển thị trong Combobox
        room_name = self.room_var.get()
        tenant_name = self.tenant_var.get()

        room_id = self.rooms_map.get(room_name, {}).get("id")
        tenant_id = self.tenants_map.get(tenant_name)

        # Trường hợp Edit: room_id/tenant_id có thể không có trong combobox (nếu phòng đang occupied)
        # Cần logic lấy ID từ selected row nếu combobox rỗng hoặc không tìm thấy map
        if self._selected_id and (room_id is None or tenant_id is None):
            # Lấy lại ID gốc từ data đang load (đơn giản hóa ở đây giả sử không đổi phòng/khách khi edit)
            # Logic đúng: Nếu muốn đổi phòng, phải chọn phòng mới từ list available.
            pass

        if room_id is None and not self._selected_id:  # Chỉ bắt buộc khi tạo mới
            messagebox.showerror("Lỗi", "Phòng không hợp lệ (có thể đã có người ở).")
            return None

        return {
            "room_id": room_id,
            "tenant_id": tenant_id,
            "contract_name": self.contact_name_var.get(),
            "start_ymd": self.start_date_var.get(),
            "end_ymd": self.end_date_var.get(),
            "rent": rent,
            "deposit_amount": deposit,
            "electric_meter_start": elec,
            "water_meter_start": water,
            "deposit_ymd": self.deposit_date_var.get(),
            "note": self.note_var.get()
        }

    def on_create(self):
        data = self._get_form_data()
        if not data: return

        try:
            create_contract(data)
            messagebox.showinfo("Thành công", "Tạo hợp đồng mới thành công!")
            self._full_reload()  # Reload để cập nhật trạng thái phòng
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

    def on_update(self):
        if not self._selected_id:
            messagebox.showwarning("Chọn", "Vui lòng chọn hợp đồng cần sửa!")
            return

        data = self._get_form_data()
        if not data: return

        # Khi update, room_id và tenant_id có thể bị None do logic combobox map
        # Cần giữ nguyên ID cũ nếu không chọn mới. (Ở đây code BE yêu cầu room_id, tenant_id)
        # Để đơn giản, bản demo này hạn chế đổi phòng/khách khi update.
        # Nếu muốn đổi, cần load lại list available room + current room.

        # Fix nhanh: Lấy room_id/tenant_id từ DB cũ nếu data trả về None
        old_contract = get_contract_by_id(self._selected_id)  # tuple
        if data["room_id"] is None: data["room_id"] = old_contract[1]
        if data["tenant_id"] is None: data["tenant_id"] = old_contract[2]

        try:
            update_contract(self._selected_id, data)
            messagebox.showinfo("Thành công", "Cập nhật hợp đồng thành công!")
            self.reload()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

    def on_delete(self):
        if not self._selected_id: return
        if messagebox.askyesno("Xác nhận", "Xóa hợp đồng này? (Phòng sẽ trống)"):
            try:
                delete_contract(self._selected_id)
                self._full_reload()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def on_export_pdf(self):
        if not self._selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng để xuất PDF!")
            return

        try:
            # Get the path to the generated PDF
            pdf_path = export_contract_to_pdf(self._selected_id)
            
            # Open the PDF file with the default application
            if os.name == 'nt':  # Windows
                os.startfile(pdf_path)
            elif os.name == 'posix':  # macOS and Linux
                if os.uname().sysname == 'Darwin':
                    os.system(f'open "{pdf_path}"')
                else:
                    os.system(f'xdg-open "{pdf_path}"')
                    
            messagebox.showinfo("Thành công", f"Đã xuất file PDF thành công!\n\nĐường dẫn: {pdf_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xuất file PDF: {str(e)}")

    def on_end_contract(self):
        if not self._selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng để kết thúc!")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn kết thúc hợp đồng này?"):
            try:
                end_contract(self._selected_id)
                messagebox.showinfo("Thành công", "Đã kết thúc hợp đồng!")
                self._full_reload()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi kết thúc hợp đồng: {str(e)}")