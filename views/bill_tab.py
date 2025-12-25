import customtkinter as ctk
from tkinter import messagebox, ttk
import time
import os
from utils.format import format_currency
from services.bill_service import (
    get_all_bills,
    get_active_contracts_with_last_bill,
    get_next_bill_month,
    bill_exists,
    create_bill,
    update_bill,
    delete_bill,
    mark_bill_paid,
    export_bill_to_pdf
)

class billTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self._selected_bill_id = None
        self._current_contract_id = None  # Lưu ID hợp đồng đang chọn để tạo bill

        # Dữ liệu cache danh sách hợp đồng active để điền form
        self.active_contracts_data = {}

        self._init_vars()
        self._build_ui()
        self._load_data()

    def _init_vars(self):
        # Biến Form
        self.search_var = ctk.StringVar()

        self.contract_select_var = ctk.StringVar()

        # Thông tin chung
        self.tenant_name_var = ctk.StringVar()
        self.room_name_var = ctk.StringVar()
        self.bill_month_var = ctk.StringVar()
        self.note_var = ctk.StringVar()

        # Chỉ số điện
        self.elec_prev_var = ctk.StringVar()
        self.elec_curr_var = ctk.StringVar()
        self.elec_price_var = ctk.StringVar()
        self.elec_total_var = ctk.StringVar()

        # Chỉ số nước
        self.water_prev_var = ctk.StringVar()
        self.water_curr_var = ctk.StringVar()
        self.water_price_var = ctk.StringVar()
        self.water_total_var = ctk.StringVar()

        # Tiền khác
        self.room_rent_var = ctk.StringVar()
        self.other_fee_var = ctk.StringVar(value="0")
        self.total_amount_var = ctk.StringVar(value="0")


    def _build_ui(self):
        # === 1. FORM NHẬP LIỆU ===
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Tiêu đề Form
        title_lbl = ctk.CTkLabel(form_frame, text="THÔNG TIN HÓA ĐƠN", font=("Arial", 16, "bold"), text_color="#333")
        title_lbl.grid(row=0, column=0, columnspan=8, pady=(10, 5))

        # --- Dòng 1: Chọn Hợp đồng & Tháng ---
        ctk.CTkLabel(form_frame, text="Chọn Hợp đồng/Phòng:", text_color="black").grid(row=1, column=0, padx=5, pady=5,
                                                                                       sticky="e")

        self.cb_contract = ttk.Combobox(form_frame, textvariable=self.contract_select_var, width=30, state="readonly")
        self.cb_contract.grid(row=1, column=1, padx=5, pady=5, sticky="w", columnspan=2)
        self.cb_contract.bind("<<ComboboxSelected>>", self.on_contract_select)

        ctk.CTkLabel(form_frame, text="Kỳ thanh toán:", text_color="black").grid(row=1, column=3, padx=5, pady=5,
                                                                                   sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.bill_month_var, width=100).grid(row=1, column=4, padx=5, pady=5,
                                                                                   sticky="w")

        # --- Dòng 2: Thông tin Readonly (Tên khách, Tiền phòng) ---
        ctk.CTkLabel(form_frame, text="Khách thuê:", text_color="black").grid(row=2, column=0, padx=5, pady=5,
                                                                              sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.tenant_name_var, state="readonly", fg_color="#eee", width=180).grid(
            row=2, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Tiền phòng cơ bản:", text_color="black").grid(row=2, column=3, padx=5, pady=5,
                                                                                     sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.room_rent_var,state="readonly",fg_color="#eee", width=120).grid(row=2, column=4, padx=5, pady=5,
                                                                                  sticky="w")

        # --- KHỐI ĐIỆN ---
        elec_frame = ctk.CTkFrame(form_frame, fg_color="#f0f9ff", border_width=1, border_color="#ccc")
        elec_frame.grid(row=3, column=0, columnspan=8, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(elec_frame, text="ĐIỆN (kWh)", font=("Arial", 12, "bold"), text_color="#0066cc").pack(side="left",
                                                                                                           padx=10)

        ctk.CTkLabel(elec_frame, text="Cũ:", text_color="black").pack(side="left", padx=2)
        ctk.CTkEntry(elec_frame, textvariable=self.elec_prev_var,state="readonly",fg_color="#eee", width=60).pack(side="left", padx=2)

        ctk.CTkLabel(elec_frame, text="Mới:", text_color="black").pack(side="left", padx=2)
        e_elec = ctk.CTkEntry(elec_frame, textvariable=self.elec_curr_var, width=60)
        e_elec.pack(side="left", padx=2)
        e_elec.bind("<KeyRelease>", self.on_recalc)  # Tự tính khi nhập

        ctk.CTkLabel(elec_frame, text="Giá:", text_color="black").pack(side="left", padx=2)
        ctk.CTkEntry(elec_frame, textvariable=self.elec_price_var, width=60).pack(side="left", padx=2)

        ctk.CTkLabel(elec_frame, text="=", text_color="black").pack(side="left", padx=2)
        ctk.CTkLabel(elec_frame, textvariable=self.elec_total_var, text_color="#cc0000",
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)

        # --- KHỐI NƯỚC ---
        water_frame = ctk.CTkFrame(form_frame, fg_color="#f0fff4", border_width=1, border_color="#ccc")
        water_frame.grid(row=4, column=0, columnspan=8, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(water_frame, text="NƯỚC (m³)", font=("Arial", 12, "bold"), text_color="#006600").pack(side="left",
                                                                                                           padx=10)

        ctk.CTkLabel(water_frame, text="Cũ:", text_color="black").pack(side="left", padx=2)
        ctk.CTkEntry(water_frame, textvariable=self.water_prev_var,state="readonly",fg_color="#eee", width=60).pack(side="left", padx=2)

        ctk.CTkLabel(water_frame, text="Mới:", text_color="black").pack(side="left", padx=2)
        e_water = ctk.CTkEntry(water_frame, textvariable=self.water_curr_var, width=60)
        e_water.pack(side="left", padx=2)
        e_water.bind("<KeyRelease>", self.on_recalc)

        ctk.CTkLabel(water_frame, text="Giá:", text_color="black").pack(side="left", padx=2)
        ctk.CTkEntry(water_frame, textvariable=self.water_price_var, width=60).pack(side="left", padx=2)

        ctk.CTkLabel(water_frame, text="=", text_color="black").pack(side="left", padx=2)
        ctk.CTkLabel(water_frame, textvariable=self.water_total_var, text_color="#cc0000",
                     font=("Arial", 12, "bold")).pack(side="left", padx=5)

        # --- Dòng 5: Phụ phí & Tổng tiền ---
        ctk.CTkLabel(form_frame, text="Phụ phí:", text_color="black").grid(row=5, column=0, padx=5, pady=10, sticky="e")
        e_other = ctk.CTkEntry(form_frame, textvariable=self.other_fee_var, width=100)
        e_other.grid(row=5, column=1, padx=5, pady=10, sticky="w")
        e_other.bind("<KeyRelease>", self.on_recalc)

        ctk.CTkLabel(form_frame, text="Ghi chú:", text_color="black").grid(row=5, column=2, padx=5, pady=10, sticky="e")
        ctk.CTkEntry(form_frame, textvariable=self.note_var, width=200).grid(row=5, column=3, columnspan=2, padx=5,
                                                                             pady=10, sticky="w")

        total_frame = ctk.CTkFrame(form_frame, fg_color="#ffe6e6")
        total_frame.grid(row=5, column=5, columnspan=2, padx=10, pady=5)
        ctk.CTkLabel(total_frame, text="TỔNG CỘNG:", font=("Arial", 12, "bold"), text_color="black").pack(side="left",
                                                                                                          padx=5)
        ctk.CTkLabel(total_frame, textvariable=self.total_amount_var, font=("Arial", 16, "bold"),
                     text_color="#cc0000").pack(side="left", padx=10)

        # --- NÚT CHỨC NĂNG FORM ---
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=6, column=0, columnspan=8, pady=10)

        ctk.CTkButton(btn_frame, text="Tính toán", command=self.on_recalc, fg_color="#6c757d", width=80).pack(
            side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Làm mới", command=self.on_clear_form, fg_color="#17a2b8", width=80).pack(side="left",
                                                                                                           padx=5)
        ctk.CTkButton(btn_frame, text="Tạo Hóa Đơn", command=self.on_create_bill, fg_color="#28a745", width=100).pack(
            side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cập Nhật", command=self.on_update_bill, fg_color="#ffc107", text_color="black",
                      width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Xóa", command=self.on_delete_bill, fg_color="#dc3545", width=80).pack(side="left",
                                                                                                        padx=5)
        ctk.CTkButton(btn_frame, text="Thanh toán", command=self.on_mark_paid, fg_color="#007bff", width=100).pack(
            side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Xuất hóa đơn", command=self._on_export_pdf, fg_color="#3498db", width=80).pack(
            side="left", padx=5)

        # === 2. BẢNG DANH SÁCH HÓA ĐƠN ===
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Thanh tìm kiếm
        search_fr = ctk.CTkFrame(table_frame, fg_color="transparent")
        search_fr.pack(fill="x", pady=5)
        ctk.CTkEntry(search_fr, textvariable=self.search_var, placeholder_text="Tìm theo phòng, tên khách...",
                     width=250).pack(side="left")
        ctk.CTkButton(search_fr, text="Tìm", command=self.on_search, width=60).pack(side="left", padx=5)
        ctk.CTkButton(search_fr, text="Tải lại", command=self._load_table_data, width=60, fg_color="gray").pack(
            side="left", padx=5)

        cols = ("id", "code", "room", "tenant", "month", "total", "status", "note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)

        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Mã HĐ")
        self.tree.heading("room", text="Phòng")
        self.tree.heading("tenant", text="Khách thuê")
        self.tree.heading("month", text="Kỳ thanh toán")
        self.tree.heading("total", text="Tổng tiền")
        self.tree.heading("status", text="Trạng thái")
        self.tree.heading("note", text="Ghi chú")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("code", width=80, anchor="center")
        self.tree.column("room", width=60, anchor="center")
        self.tree.column("tenant", width=150)
        self.tree.column("month", width=80, anchor="center")
        self.tree.column("total", width=100, anchor="e")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("note", width=150)

        # Scrollbar
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=sb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

    # === LOGIC LOAD DATA ===

    def _load_data(self):
        self._load_active_contracts()
        self._load_table_data()

    def _load_active_contracts(self):
        contracts = get_active_contracts_with_last_bill()
        values = []
        self.active_contracts_data = {}

        for c in contracts:
            c_id = c[0]
            room_id = c[1]
            room_name = c[2]
            tenant_name = c[3]
            room_rent_amount = c[4]
            display_str = f"{room_name} - {tenant_name}"
            values.append(display_str)
            self.active_contracts_data[display_str] = {
                "contract_id": c_id,
                "room_id": room_id,
                "room_name": room_name,
                "tenant_name": tenant_name,
                "room_rent_amount": c[4],
                "elec_price": c[5],
                "water_price": c[6],
                "elec_prev": c[9],
                "water_prev": c[10]
            }
        self.cb_contract['values'] = values

    def _load_table_data(self):
        # Clear bảng
        for item in self.tree.get_children():
            self.tree.delete(item)

        bills = get_all_bills()
        filter_kw = self.search_var.get().lower()

        for b in bills:
            b_id = b[0]
            b_code = b[1]
            b_month = b[3]
            b_total = b[11]
            b_note = b[12]
            b_status = b[-1]

            # Cột join
            b_room = b[-4]
            b_tenant = b[-3]


            status_display = {
                'paid': 'Đã thanh toán',
                'unpaid': 'Chưa thanh toán',
                'cancelled': 'Đã hủy'
            }.get(b_status, b_status)

            if filter_kw and (filter_kw not in str(b_code).lower() and 
                             filter_kw not in b_room.lower() and 
                             filter_kw not in b_tenant.lower()):
                continue

            self.tree.insert("", "end", values=(
                b_id, b_code, b_room, b_tenant, b_month, 
                format_currency(b_total), status_display, b_note
            ))

    def on_contract_select(self, event):
        selection = self.contract_select_var.get()
        if not selection or selection not in self.active_contracts_data:
            return

        data = self.active_contracts_data[selection]
        self._current_contract_id = data["contract_id"]

        # Fill thông tin
        self.tenant_name_var.set(data["tenant_name"])
        self.room_name_var.set(data["room_name"])
        self.room_rent_var.set(int(data["room_rent_amount"]))

        self.elec_price_var.set(int(data["elec_price"]))
        self.water_price_var.set(int(data["water_price"]))

        self.elec_prev_var.set(int(data["elec_prev"]))
        self.water_prev_var.set(int(data["water_prev"]))

        # Clear chỉ số mới
        self.elec_curr_var.set("")
        self.water_curr_var.set("")

        # Gợi ý tháng tiếp theo
        next_month = get_next_bill_month(self._current_contract_id)
        self.bill_month_var.set(next_month)

        self.on_recalc()

    def on_recalc(self, event=None):
        """Tính toán tổng tiền realtime"""
        try:
            e_old = float(self.elec_prev_var.get() or 0)
            e_new = float(self.elec_curr_var.get() or 0)
            e_price = float(self.elec_price_var.get() or 0)

            w_old = float(self.water_prev_var.get() or 0)
            w_new = float(self.water_curr_var.get() or 0)
            w_price = float(self.water_price_var.get() or 0)

            rent = float(self.room_rent_var.get() or 0)
            other = float(self.other_fee_var.get() or 0)

            # Tính tiêu thụ (không âm)
            e_used = max(0, e_new - e_old)
            w_used = max(0, w_new - w_old)

            e_total = e_used * e_price
            w_total = w_used * w_price

            total = rent + e_total + w_total + other

            # Update UI
            self.elec_total_var.set(format_currency(e_total))
            self.water_total_var.set(format_currency(w_total))
            self.total_amount_var.set(format_currency(total) + " VND")

        except ValueError:
            pass

    def on_create_bill(self):
        if not self._current_contract_id:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn hợp đồng trước!")
            return

        month = self.bill_month_var.get().strip()
        if not month:
            messagebox.showwarning("Lỗi", "Vui lòng nhập tháng (MM/YYYY)!")
            return

        # Check trùng
        if bill_exists(self._current_contract_id, month):
            messagebox.showerror("Lỗi", f"Hóa đơn tháng {month} cho phòng này đã tồn tại!")
            return

        try:
            e_prev = float(self.elec_prev_var.get() or 0)
            e_curr = float(self.elec_curr_var.get() or 0)
            w_prev = float(self.water_prev_var.get() or 0)
            w_curr = float(self.water_curr_var.get() or 0)

            if e_curr < e_prev:
                messagebox.showerror("Lỗi", "Chỉ số điện mới không được nhỏ hơn chỉ số cũ!")
                return
            if w_curr < w_prev:
                messagebox.showerror("Lỗi", "Chỉ số nước mới không được nhỏ hơn chỉ số cũ!")
                return

            # Tạo mã bill
            bill_id = f"B{self._current_contract_id}_{int(time.time())}"

            data = {
                "bill_id": bill_id,
                "contract_id": self._current_contract_id,
                "bill_month": month,
                "tenant_name": self.tenant_name_var.get(),
                "room_id": self.active_contracts_data[self.contract_select_var.get()]["room_id"],
                "room_name": self.room_name_var.get(),
                "elec_prev": e_prev,
                "elec_current": e_curr,
                "water_prev": w_prev,
                "water_current": w_curr,
                "electric_unit_price": float(self.elec_price_var.get()),
                "water_unit_price": float(self.water_price_var.get()),
                "room_rent_amount": float(self.room_rent_var.get()),
                "other_fee": float(self.other_fee_var.get() or 0),
                "note": self.note_var.get()
            }

            create_bill(data)
            messagebox.showinfo("Thành công", "Đã tạo hóa đơn mới!")
            self.on_clear_form()
            self._load_table_data()  # Reload bảng

        except ValueError:
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng kiểm tra lại các trường số!")
        except Exception as e:
            messagebox.showerror("Lỗi hệ thống", str(e))

    def on_update_bill(self):
        if not self._selected_bill_id:
            messagebox.showwarning("Chọn", "Vui lòng chọn hóa đơn cần sửa trong bảng!")
            return
        try:
            data = {
                "bill_month": self.bill_month_var.get(),
                "elec_prev": float(self.elec_prev_var.get()),
                "elec_current": float(self.elec_curr_var.get()),
                "water_prev": float(self.water_prev_var.get()),
                "water_current": float(self.water_curr_var.get()),
                "electric_unit_price": float(self.elec_price_var.get()),
                "water_unit_price": float(self.water_price_var.get()),
                "room_rent_amount": float(self.room_rent_var.get()),
                "other_fee": float(self.other_fee_var.get() or 0),
                "note": self.note_var.get()
            }
            update_bill(self._selected_bill_id, data)
            messagebox.showinfo("Thành công", "Cập nhật hóa đơn thành công!")
            self.on_clear_form()
            self._load_table_data()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def on_delete_bill(self):
        if not self._selected_bill_id:
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa hóa đơn này?"):
            try:
                delete_bill(self._selected_bill_id)
                self.on_clear_form()
                self._load_table_data()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def on_mark_paid(self):
        if not self._selected_bill_id:
            messagebox.showwarning("Chọn", "Vui lòng chọn hóa đơn để thanh toán!")
            return

        if messagebox.askyesno("Xác nhận", "Xác nhận khách đã thanh toán đủ tiền?"):
            try:
                mark_bill_paid(self._selected_bill_id)
                messagebox.showinfo("Thành công", "Đã cập nhật trạng thái: Đã thanh toán!")
                self._load_table_data()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

    def on_search(self):
        self._load_table_data()

    def on_select_row(self, event):
        sel = self.tree.selection()
        if not sel: return

        # Lấy row
        item = self.tree.item(sel[0])
        val = item['values']

        self._selected_bill_id = val[0]
        self.tenant_name_var.set(val[3])
        self.bill_month_var.set(val[4])
        self.note_var.set(val[7])

    def _on_export_pdf(self):
        """Xuất hóa đơn ra file PDF"""
        if not self._selected_bill_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn hóa đơn cần xuất!")
            return
            
        try:
            pdf_path = export_bill_to_pdf(self._selected_bill_id)
            if pdf_path and os.path.exists(pdf_path):
                messagebox.showinfo("Thành công", "Đã xuất hóa đơn thành công")
            else:
                messagebox.showerror("Lỗi", "Không thể xuất hóa đơn. Vui lòng thử lại!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra khi xuất hóa đơn: {str(e)}")

    def on_clear_form(self):
        self._selected_bill_id = None
        self._current_contract_id = None
        self.contract_select_var.set("")
        self.tenant_name_var.set("")
        self.room_name_var.set("")
        self.bill_month_var.set("")
        self.note_var.set("")
        
        # Reset các trường số
        self.elec_prev_var.set("0")
        self.elec_curr_var.set("")
        self.elec_price_var.set("0")
        self.elec_total_var.set("0")
        
        self.water_prev_var.set("0")
        self.water_curr_var.set("")
        self.water_price_var.set("0")
        self.water_total_var.set("0")
        
        self.room_rent_var.set("0")
        self.other_fee_var.set("0")
        self.total_amount_var.set("0")
        
        vars_to_clear = [
            self.tenant_name_var, self.bill_month_var, self.note_var,
            self.elec_prev_var, self.elec_curr_var, self.elec_price_var, self.elec_total_var,
            self.water_prev_var, self.water_curr_var, self.water_price_var, self.water_total_var,
            self.room_rent_var, self.other_fee_var, self.total_amount_var
        ]
        for v in vars_to_clear:
            v.set("")
        self.other_fee_var.set("0")
        self.total_amount_var.set("0")

        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])