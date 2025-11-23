
# models/bill_model.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


@dataclass
@dataclass
class BillDTO:
    id: int | None
    tenant_name: str
    room_code: str
    month: str
    elec_prev: int | None
    elec_current: int | None
    water_prev: int | None
    water_current: int | None
    water_unit_price: int | None
    electric_unit_price: int | None
    room_rent_amount: int | None
    other_fee: int | None
    total_amount: int
    paid_amount: int
    paid_status: int  # 0/1/2
    paid_ymd: str | None
    note: str | None




class BillService:
    """
    Service in-memory, giống Room/Tenant Service.
    Sau này đổi sang SQLite cũng giữ nguyên interface này.
    """
    def __init__(self):
        self._data: list[BillDTO] = []
        self._auto = 1
        root = Path(__file__).resolve().parent.parent  # models/ -> project root
        self._export_dir = root / "exports"
        self._export_dir.mkdir(exist_ok=True)

    # -------------------- LIST --------------------
    def list(self, keyword: str | None = None) -> list[BillDTO]:
        if not keyword:
            return list(self._data)

        kw = keyword.lower()
        return [
            b for b in self._data
            if kw in b.tenant_name.lower()
            or kw in b.room_code.lower()
            or kw in b.month.lower()
            or (b.note and kw in b.note.lower())
        ]

    # -------------------- CREATE --------------------
    def create(self, **fields) -> BillDTO:
        tenant_name = fields.get("tenant_name", "").strip()
        month = fields.get("month", "")

        if not tenant_name:
            raise ValueError("Tên khách không được trống")
        if not month or len(month) != 7:
            raise ValueError("Tháng phải dạng YYYY-MM")

        # Tính tiền điện, nước, tổng
        total = self._recalc_total(fields)

        dto = BillDTO(
            id=self._auto,
            tenant_name=tenant_name,
            room_code=fields.get("room_code", "").strip(),
            month=month,

            elec_prev=fields.get("elec_prev"),
            elec_current=fields.get("elec_current"),

            water_prev=fields.get("water_prev"),
            water_current=fields.get("water_current"),

            water_unit_price=fields.get("water_unit_price"),
            electric_unit_price=fields.get("electric_unit_price"),

            room_rent_amount=fields.get("room_rent_amount"),
            other_fee=fields.get("other_fee"),

            total_amount=total,

            paid_amount=fields.get("paid_amount", 0),
            paid_status=fields.get("paid_status", 0),
            paid_ymd=fields.get("paid_ymd"),

            note=fields.get("note"),
        )
        self._auto += 1
        self._data.append(dto)
        return dto

    # -------------------- UPDATE --------------------
    def update(self, bill_id: int, **fields) -> BillDTO:
        b = self._get(bill_id)

        # Cập nhật từng field nếu được truyền vào
        for key, value in fields.items():
            if hasattr(b, key):
                setattr(b, key, value)

        # Nếu các field dùng để tính tổng thay đổi → tính lại total
        if any(k in fields for k in (
            "elec_prev", "elec_current",
            "water_prev", "water_current",
            "water_unit_price", "electric_unit_price",
            "room_rent_amount", "other_fee",
        )):
            b.total_amount = self._recalc_total(b.__dict__)

        # Nếu cập nhật paid_amount → tự tính paid_status
        if "paid_amount" in fields:
            if b.paid_amount >= b.total_amount:
                b.paid_status = 2
            elif b.paid_amount > 0:
                b.paid_status = 1
            else:
                b.paid_status = 0

        return b

    # -------------------- DELETE --------------------
    def delete(self, bill_id: int):
        self._data = [x for x in self._data if x.id != bill_id]

    # -------------------- INTERNAL --------------------
    def _get(self, bill_id: int) -> BillDTO:
        for b in self._data:
            if b.id == bill_id:
                return b
        raise ValueError("Không tìm thấy hóa đơn")

    def _recalc_total(self, f) -> int:
        """
        f có thể là dict hoặc BillDTO.__dict__
        """
        # Điện
        if f.get("elec_prev") is not None and f.get("elec_current") is not None:
            elec_amount = (f["elec_current"] - f["elec_prev"]) * (f.get("electric_unit_price") or 0)
        else:
            elec_amount = 0

        # Nước
        if f.get("water_prev") is not None and f.get("water_current") is not None:
            water_amount = (f["water_current"] - f["water_prev"]) * (f.get("water_unit_price") or 0)
        else:
            water_amount = 0

        total = (
            (f.get("room_rent_amount") or 0) +
            (f.get("other_fee") or 0) +
            elec_amount +
            water_amount
        )
        return total


    def export_pdf(self, bill_id: int) -> Path:
        """Tạo file PDF cho 1 bill, trả về đường dẫn file."""
        b = self._get(bill_id)

        # tên file: exports/bill_0001_2025-01.pdf
        safe_month = (b.month or "").replace("/", "-")
        filename = self._export_dir / f"bill_{b.id:04d}_{safe_month}.pdf"

        c = canvas.Canvas(str(filename), pagesize=A4)
        width, height = A4
        y = height - 40

        # ===== Header =====
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, "RENTAL BILL")
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Bill ID: {b.id}")
        y -= 15
        c.drawString(40, y, f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 25

        # ===== Thông tin khách / phòng =====
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Customer / Room")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Customer : {b.tenant_name}")
        y -= 15
        c.drawString(60, y, f"Room     : {b.room_code}")
        y -= 15
        c.drawString(60, y, f"Month    : {b.month}")
        y -= 25

        # ===== Điện =====
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Electricity")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Prev      : {b.elec_prev or 0}")
        y -= 15
        c.drawString(60, y, f"Current   : {b.elec_current or 0}")
        y -= 15
        c.drawString(60, y, f"Unit price: {b.electric_unit_price or 0} VND")
        y -= 25

        # ===== Nước =====
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Water")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Prev      : {b.water_prev or 0}")
        y -= 15
        c.drawString(60, y, f"Current   : {b.water_current or 0}")
        y -= 15
        c.drawString(60, y, f"Unit price: {b.water_unit_price or 0} VND")
        y -= 25

        # ===== Tiền phòng + fee khác =====
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Room / Other")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Room rent : {b.room_rent_amount or 0:,.0f} VND")
        y -= 15
        c.drawString(60, y, f"Other fee : {b.other_fee or 0:,.0f} VND")
        y -= 25

        # ===== Tổng & thanh toán =====
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Payment")
        y -= 18
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Total amount : {b.total_amount:,.0f} VND")
        y -= 15
        c.drawString(60, y, f"Paid amount  : {b.paid_amount:,.0f} VND")
        y -= 15

        status_text = {0: "Unpaid", 1: "Partial", 2: "Paid"}.get(b.paid_status, "Unpaid")
        c.drawString(60, y, f"Status       : {status_text}")
        y -= 15
        c.drawString(60, y, f"Paid date    : {b.paid_ymd or '-'}")
        y -= 25

        # ===== Ghi chú =====
        if b.note:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Note")
            y -= 18
            c.setFont("Helvetica", 10)
            c.drawString(60, y, b.note[:100])  # cắt cho chắc, khỏi tràn
            y -= 20

        # Footer
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(40, 40, "Generated by Rental Manager")

        c.showPage()
        c.save()
        return filename