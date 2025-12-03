from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from database.db import get_connection


@dataclass
class BillDTO:
    id: int | None
    tenant_name: str
    room_no: str
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


class BillModel:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

        root = Path(__file__).resolve().parent.parent  # models/ -> project root
        self._export_dir = root / "exports"
        self._export_dir.mkdir(exist_ok=True)

    # ---------- mapping ----------
    def _row_to_dto(self, row: sqlite3.Row) -> BillDTO:
        d = dict(row)
        return BillDTO(
            id=d["bill_id"],                     # map từ bill_id trong DB
            tenant_name=d["tenant_name"],
            room_no=d["room_no"],
            month=d["month"],
            elec_prev=d["elec_prev"],
            elec_current=d["elec_current"],
            water_prev=d["water_prev"],
            water_current=d["water_current"],
            water_unit_price=d["water_unit_price"],
            electric_unit_price=d["electric_unit_price"],
            room_rent_amount=d["room_rent_amount"],
            other_fee=d["other_fee"],
            total_amount=d["total_amount"],
            paid_amount=d["paid_amount"],
            paid_status=d["paid_status"],
            paid_ymd=d["paid_ymd"],
            note=d["note"],
        )

    # ---------- Query ----------
    def list(self, keyword: str | None = None) -> List[BillDTO]:
        sql = "SELECT * FROM bill"
        params: list = []

        if keyword:
            sql += " WHERE tenant_name LIKE ? OR room_no LIKE ? OR month LIKE ? OR note LIKE ?"
            kw = f"%{keyword}%"
            params = [kw, kw, kw, kw]

        sql += " ORDER BY bill_id DESC"
        cur = self.conn.execute(sql, params)
        return [self._row_to_dto(r) for r in cur.fetchall()]

    def get(self, bill_id: int) -> BillDTO:
        cur = self.conn.execute("SELECT * FROM bill WHERE bill_id = ?", (bill_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Không tìm thấy hóa đơn")
        return self._row_to_dto(row)

    # ---------- Commands ----------
    def create(self, **fields) -> BillDTO:
        tenant_name = fields.get("tenant_name", "").strip()
        month = fields.get("month", "")

        if not tenant_name:
            raise ValueError("Tên khách không được trống")
        if not month or len(month) != 6:
            raise ValueError("Tháng phải dạng YYYYMM")

        total = self._recalc_total(fields)

        cur = self.conn.execute(
            """
            INSERT INTO bill (
                tenant_name, room_no, month,
                elec_prev, elec_current,
                water_prev, water_current,
                water_unit_price, electric_unit_price,
                room_rent_amount, other_fee,
                total_amount,
                paid_amount, paid_status, paid_ymd,
                note
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                fields.get("tenant_name"),
                fields.get("room_no", "").strip(),
                month,
                fields.get("elec_prev"),
                fields.get("elec_current"),
                fields.get("water_prev"),
                fields.get("water_current"),
                fields.get("water_unit_price"),
                fields.get("electric_unit_price"),
                fields.get("room_rent_amount"),
                fields.get("other_fee"),
                total,
                fields.get("paid_amount", 0),
                fields.get("paid_status", 0),
                fields.get("paid_ymd"),
                fields.get("note"),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def update(self, bill_id: int, **fields) -> BillDTO:
        b = self.get(bill_id)

        data = b.__dict__ | fields

        if any(
            k in fields
            for k in (
                "elec_prev",
                "elec_current",
                "water_prev",
                "water_current",
                "water_unit_price",
                "electric_unit_price",
                "room_rent_amount",
                "other_fee",
            )
        ):
            data["total_amount"] = self._recalc_total(data)

        # nếu có paid_amount → cập nhật paid_status
        if "paid_amount" in fields:
            if data["paid_amount"] >= data["total_amount"]:
                data["paid_status"] = 2
            elif data["paid_amount"] > 0:
                data["paid_status"] = 1
            else:
                data["paid_status"] = 0

        self.conn.execute(
            """
            UPDATE bill
            SET tenant_name = ?, room_no = ?, month = ?,
                elec_prev = ?, elec_current = ?,
                water_prev = ?, water_current = ?,
                water_unit_price = ?, electric_unit_price = ?,
                room_rent_amount = ?, other_fee = ?,
                total_amount = ?, paid_amount = ?, paid_status = ?,
                paid_ymd = ?, note = ?
            WHERE bill_id = ?
            """,
            (
                data["tenant_name"],
                data["room_no"],
                data["month"],
                data["elec_prev"],
                data["elec_current"],
                data["water_prev"],
                data["water_current"],
                data["water_unit_price"],
                data["electric_unit_price"],
                data["room_rent_amount"],
                data["other_fee"],
                data["total_amount"],
                data["paid_amount"],
                data["paid_status"],
                data["paid_ymd"],
                data["note"],
                bill_id,
            ),
        )
        self.conn.commit()
        return self.get(bill_id)

    def delete(self, bill_id: int) -> None:
        self.conn.execute("DELETE FROM bill WHERE bill_id = ?", (bill_id,))
        self.conn.commit()

    # ---------- internal calc ----------
    def _recalc_total(self, f) -> int:
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
            (f.get("room_rent_amount") or 0)
            + (f.get("other_fee") or 0)
            + elec_amount
            + water_amount
        )
        return total

    # ---------- export ----------
    def export_pdf(self, bill_id: int) -> Path:
        """Tạo file PDF cho 1 bill, trả về đường dẫn file."""
        b = self.get(bill_id)

        safe_month = (b.month or "").replace("/", "-")
        filename = self._export_dir / f"bill_{b.id:04d}_{safe_month}.pdf"

        c = canvas.Canvas(str(filename), pagesize=A4)
        width, height = A4

        margin_x = 25 * mm
        content_w = width - 2 * margin_x
        y = height - 30 * mm

        # ===== Header ngoài cùng =====
        c.setLineWidth(1)
        c.roundRect(margin_x, y - 20 * mm, content_w, 18 * mm, 5, stroke=1, fill=0)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(margin_x + 8, y, "RENTAL BILL")

        c.setFont("Helvetica", 10)
        c.drawRightString(margin_x + content_w - 8, y,
                          f"Bill ID: {b.id}   Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        y -= 25 * mm

        # helper vẽ box + title
        def section_box(title: str, box_height_mm: float) -> float:
            nonlocal y
            box_h = box_height_mm * mm
            # khung
            c.roundRect(margin_x, y - box_h, content_w, box_h, 4, stroke=1, fill=0)
            # title
            c.setFont("Helvetica-Bold", 11)
            c.drawString(margin_x + 6, y - 6, title)
            # trả về y_text (bên trong box, trừ title)
            return y - 16

        # ===== Customer / Room =====
        y_text = section_box("Customer / Room", box_height_mm=22)
        c.setFont("Helvetica", 10)
        c.drawString(margin_x + 12, y_text, f"Customer : {b.tenant_name}")
        c.drawString(margin_x + 12, y_text - 12, f"Room     : {b.room_no}")
        c.drawString(margin_x + 12, y_text - 24, f"Month    : {b.month}")
        y -= 22 * mm + 4  # xuống dưới box + thêm khoảng cách

        # ===== Electricity =====
        y_text = section_box("Electricity", box_height_mm=22)
        c.setFont("Helvetica", 10)
        c.drawString(margin_x + 12, y_text, f"Prev      : {b.elec_prev or 0}")
        c.drawString(margin_x + 12, y_text - 12, f"Current   : {b.elec_current or 0}")
        c.drawString(margin_x + 12, y_text - 24, f"Unit price: {b.electric_unit_price or 0} VND")
        y -= 22 * mm + 4

        # ===== Water =====
        y_text = section_box("Water", box_height_mm=22)
        c.setFont("Helvetica", 10)
        c.drawString(margin_x + 12, y_text, f"Prev      : {b.water_prev or 0}")
        c.drawString(margin_x + 12, y_text - 12, f"Current   : {b.water_current or 0}")
        c.drawString(margin_x + 12, y_text - 24, f"Unit price: {b.water_unit_price or 0} VND")
        y -= 22 * mm + 4

        # ===== Room / Other =====
        y_text = section_box("Room / Other", box_height_mm=18)
        c.setFont("Helvetica", 10)
        c.drawString(margin_x + 12, y_text, f"Room rent : {b.room_rent_amount or 0:,.0f} VND")
        c.drawString(margin_x + 12, y_text - 12, f"Other fee : {b.other_fee or 0:,.0f} VND")
        y -= 18 * mm + 4

        # ===== Payment =====
        y_text = section_box("Payment", box_height_mm=24)
        c.setFont("Helvetica", 10)
        c.drawString(margin_x + 12, y_text, f"Total amount : {b.total_amount:,.0f} VND")
        c.drawString(margin_x + 12, y_text - 12, f"Paid amount  : {b.paid_amount:,.0f} VND")
        status_text = {0: "Unpaid", 1: "Partial", 2: "Paid"}.get(b.paid_status, "Unpaid")
        c.drawString(margin_x + 12, y_text - 24, f"Status       : {status_text}")
        c.drawString(margin_x + 12, y_text - 36, f"Paid date    : {b.paid_ymd or '-'}")
        y -= 24 * mm + 4

        # ===== Note (nếu có) =====
        if b.note:
            y_text = section_box("Note", box_height_mm=18)
            c.setFont("Helvetica", 10)
            c.drawString(margin_x + 12, y_text, b.note[:100])
            y -= 18 * mm + 4

        # footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(margin_x, 15 * mm, "Generated by Rental Manager")

        c.showPage()
        c.save()
        return filename
