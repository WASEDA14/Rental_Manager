# views/contract_tab.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os
import sys
import subprocess
from utils.format import format_currency, parse_currency, format_money
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


class contractTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._selected_id = None

        # Cache dữ liệu cho Combobox (ID -> Data)
        self.rooms_map = {}
        self.tenants_map = {}

        # ===== Variables =====
        self.room_var = ctk.StringVar()
        self.tenant_var = ctk.StringVar()
        self.rent_var = ctk.StringVar()
        self.deposit_var = ctk.StringVar()
        self.start_date_var = ctk.StringVar()
        self.end_date_var = ctk.StringVar()
        self.deposit_date_var = ctk.StringVar()
        import datetime
        self.deposit_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))

        self.elec_start_var = ctk.StringVar(value="0")
        self.water_start_var = ctk.StringVar(value="0")
        self.note_var = ctk.StringVar()
        self.search_var = ctk.StringVar()

        # ===== UI Layout =====
        self._build_form()
        self._build_table()
        # self._build_actions()

        # Load Data
        self.initialize()
        
    def initialize(self):
        self.on_clear()
        self._load_combobox_data()
        self.reload()


    def _build_form(self):
        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=12, pady=(12, 6))

        # --- Row 0 ---
        ctk.CTkLabel(form, text="Phòng *").grid(row=0, column=0, sticky="w")
        self.cb_room = ctk.CTkComboBox(form, width=160, variable=self.room_var, command=self.on_room_select)
        self.cb_room.grid(row=0, column=1, padx=6)

        ctk.CTkLabel(form, text="Khách thuê *").grid(row=0, column=2, sticky="w")
        self.cb_tenant = ctk.CTkComboBox(form, width=160, variable=self.tenant_var, command=self.on_tenant_select)
        self.cb_tenant.grid(row=0, column=3, padx=6)

        # --- Row 1 ---
        ctk.CTkLabel(form, text="Giá thuê").grid(row=1, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.rent_var, state="readonly", fg_color="#eee", width=160).grid(row=1,
                                                                                                          column=1,
                                                                                                          padx=6)

        ctk.CTkLabel(form, text="Tiền cọc").grid(row=1, column=2, sticky="w")
        entry_deposit = ctk.CTkEntry(form, textvariable=self.deposit_var, width=160)
        entry_deposit.grid(row=1, column=3, padx=6)
        entry_deposit.bind("<KeyRelease>", lambda e: format_money(self, e))

        ctk.CTkLabel(form, text="Ngày cọc").grid(row=1, column=4, sticky="w")
        self.deposit_date_entry = DateEntry(form, textvariable=self.deposit_date_var, width=16,
                                            date_pattern="dd/mm/yyyy")
        self.deposit_date_entry.grid(row=1, column=5, padx=6, sticky="w")

        # --- Row 2 ---
        ctk.CTkLabel(form, text="Ngày bắt đầu").grid(row=2, column=0, sticky="w")
        DateEntry(form, textvariable=self.start_date_var, width=16, date_pattern="dd/mm/yyyy").grid(row=2, column=1,
                                                                                                    padx=6, sticky="w")

        ctk.CTkLabel(form, text="Ngày kết thúc").grid(row=2, column=2, sticky="w")
        DateEntry(form, textvariable=self.end_date_var, width=16, date_pattern="dd/mm/yyyy").grid(row=2, column=3,
                                                                                                  padx=6, sticky="w")

        # --- Row 3 ---
        ctk.CTkLabel(form, text="Điện đầu (kWh)").grid(row=3, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.elec_start_var, width=160).grid(row=3, column=1, padx=6)

        ctk.CTkLabel(form, text="Nước đầu (m³)").grid(row=3, column=2, sticky="w")
        ctk.CTkEntry(form, textvariable=self.water_start_var, width=160).grid(row=3, column=3, padx=6)

        # --- Row 4 ---
        ctk.CTkLabel(form, text="Ghi chú").grid(row=4, column=0, sticky="w")
        ctk.CTkEntry(form, textvariable=self.note_var, width=500).grid(row=4, column=1, columnspan=6, padx=6,
                                                                       sticky="we")

        # Action buttons and search
        action = ctk.CTkFrame(form, fg_color="transparent")
        action.grid(row=5, column=0, columnspan=8, pady=(10, 0), sticky="ew")

        ctk.CTkLabel(action, text="Tìm kiếm").pack(side="left")
        ctk.CTkEntry(action, textvariable=self.search_var, width=200).pack(side="left", padx=6)
        ctk.CTkButton(action, text="Tìm", width=60, command=self.reload).pack(side="left")

        ctk.CTkButton(action, text="Xuất hợp đồng", fg_color="#3498db", command=self.on_export_pdf).pack(side="right",
                                                                                                         padx=6)
        ctk.CTkButton(action, text="Kết thúc HĐ", fg_color="#8e44ad", command=self.on_end_contract).pack(side="right",
                                                                                                         padx=6)
        ctk.CTkButton(action, text="Xóa", fg_color="#e74c3c", command=self.on_delete).pack(side="right", padx=6)
        ctk.CTkButton(action, text="Cập nhật", fg_color="#f39c12", command=self.on_update).pack(side="right", padx=6)
        ctk.CTkButton(action, text="Thêm mới", fg_color="#27ae60", command=self.on_create).pack(side="right", padx=6)
        ctk.CTkButton(action, text="Làm mới", fg_color="#7f8c8d", command=self.on_clear).pack(side="right", padx=6)

    def _build_table(self):
        # Treeview frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Define columns and headers
        cols = ("id", "room", "tenant", "start", "end", "rent", "status")
        headers = {
            "id": "ID",
            "room": "Phòng",
            "tenant": "Khách thuê",
            "start": "Bắt đầu",
            "end": "Kết thúc",
            "rent": "Giá thuê",
            "status": "Trạng thái"
        }

        # Configure column widths and anchors
        widths = {
            "id": 40,
            "room": 80,
            "tenant": 150,
            "start": 100,
            "end": 100,
            "rent": 100,
            "status": 100
        }
        anchors = {
            "id": "center",
            "room": "center",
            "tenant": "w",
            "start": "center",
            "end": "center",
            "rent": "e",
            "status": "center"
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
        self.tree.bind("<<TreeviewSelect>>", self.on_pick)

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

    def _reload(self):
        self._load_combobox_data()
        self.reload()
        self.on_clear()

    # ===== Event Handlers =====

    def on_room_select(self, choice):
        # Tự động điền giá thuê khi chọn phòng
        if choice in self.rooms_map:
            rent = self.rooms_map[choice]["rent"]
            self.rent_var.set(format_currency(rent))

    def on_tenant_select(self, choice):
        # Tự động điền người liên hệ là tên khách thuê
        self.tenant_var.set(choice)

    def on_pick(self, _):
        sel = self.tree.selection()
        if not sel: return

        item = self.tree.item(sel[0])
        self._selected_id = int(item["values"][0])

        contract = get_contract_by_id(self._selected_id)
        if contract:
            self.room_var.set(contract['room_name'])
            self.tenant_var.set(contract['full_name'])
            self.rent_var.set(format_currency(contract['rent']))
            self.deposit_var.set(format_currency(contract['deposit_amount']))
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
        # self.contract_name_var.set("")
        self.rent_var.set("")
        self.deposit_var.set("")
        self.start_date_var.set("")
        self.end_date_var.set("")
        # Set deposit date to today when clearing the form
        import datetime
        self.deposit_date_var.set(datetime.date.today().strftime("%Y-%m-%d"))
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
            rent = parse_currency(self.rent_var.get())
            deposit = parse_currency(self.deposit_var.get() or 0)
            elec = int(self.elec_start_var.get() or 0)
            water = int(self.water_start_var.get() or 0)
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Giá tiền, Điện, Nước phải là số!")
            return None

        # Lấy ID từ tên hiển thị
        room_name = self.room_var.get()
        tenant_name = self.tenant_var.get()

        room_id = self.rooms_map.get(room_name, {}).get("id")
        tenant_id = self.tenants_map.get(tenant_name)

        if self._selected_id and (room_id is None or tenant_id is None):
            pass

        if room_id is None and not self._selected_id:
            messagebox.showerror("Lỗi", "Phòng không hợp lệ (có thể đã có người ở).")
            return None

        return {
            "room_id": room_id,
            "tenant_id": tenant_id,
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
            self._reload()  # Reload để cập nhật trạng thái phòng
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

    def on_update(self):
        if not self._selected_id:
            messagebox.showwarning("Chọn", "Vui lòng chọn hợp đồng cần sửa!")
            return

        data = self._get_form_data()
        if not data: return


        old_contract = get_contract_by_id(self._selected_id)  # tuple
        if data["room_id"] is None: data["room_id"] = old_contract[1]
        if data["tenant_id"] is None: data["tenant_id"] = old_contract[2]

        try:
            update_contract(self._selected_id, data)
            messagebox.showinfo("Thành công", "Cập nhật hợp đồng thành công!")
            self._reload()
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

    def on_delete(self):
        if not self._selected_id: return
        if messagebox.askyesno("Xác nhận", "Xóa hợp đồng này? (Phòng sẽ trống)"):
            try:
                delete_contract(self._selected_id)
                self._reload()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def on_export_pdf(self):
        if not self._selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hợp đồng để xuất PDF!")
            return
        try:
            pdf_path = export_contract_to_pdf(self._selected_id)
            
            if pdf_path and os.path.exists(pdf_path):
                # Mở file PDF bằng ứng dụng mặc định
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
                elif os.name == 'posix':  # macOS and Linux
                    if sys.platform == 'darwin':
                        subprocess.run(['open', pdf_path], check=True)
                    else:
                        subprocess.run(['xdg-open', pdf_path], check=True)
                messagebox.showinfo("Thành công", f"Xuất hợp đồng thành công:\n{pdf_path}")
            else:
                messagebox.showerror("Lỗi", "Không thể xuất hợp đồng. Vui lòng thử lại!")
                
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
                self.reload()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi kết thúc hợp đồng: {str(e)}")