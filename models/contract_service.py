# contract_service.py
import re
from dataclasses import dataclass
import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from database.db import get_connection


@dataclass
class ContractDTO:
     contract_id: str
     room_no: int
     tenant_id: int
     start_ymd: str
     end_ymd: Optional[str]
     deposit_amount: int
     electric_meter_start: int
     water_meter_start : int
     deposit_ymd : str
     note: Optional[str]
     contract_name : str
     contract_status: int = 1
     is_deleted: int = 0

class contractModel:
    def __init__(self):
            self.conn = get_connection()
            self.conn.row_factory = sqlite3.Row
            root = Path(__file__).resolve().parent.parent
            self._export_dir = root / "exports"
            self._export_dir.mkdir(exist_ok=True)

            # ---------- mapping ----------
    def _row_to_dto(self, row: sqlite3.Row) -> ContractDTO:
            d = dict(row)
            return ContractDTO(
                contract_id = d["contract_id"],
                room_no = d["room_no"],
                tenant_id = d["tenant_id"],
                start_ymd = d["start_ymd"],
                end_ymd = d["end_ymd"],
                deposit_amount = d["deposit_amount"],
                electric_meter_start = d["electric_meter_start"],
                water_meter_start = d["water_meter_start"],
                contract_status = d["contract_status"],
                deposit_ymd = d["deposit_ymd"],
                note = d["note"],
                contract_name = d["contract_name"],
                is_deleted = d["is_deleted"],
            )

            # ---------- Query ----------

    def list(self, keyword: str | None = None) -> List[Dict[str, Any]]:
        """
        Trả về list[dict] cho UI. Nếu keyword có giá trị sẽ tìm theo contract_name, contract_id hoặc tenant_name.
        Điều quan trọng: chỉ thêm placeholders (?) khi có params tương ứng.
        """
        sql = """
        SELECT
            c.contract_id AS id,
            c.contract_id AS contract_no,
            COALESCE(t.full_name, '') AS tenant,
            c.room_no AS room,
            c.start_ymd AS start,
            c.end_ymd AS end,
            COALESCE(c.deposit_amount, 0) AS deposit,
            COALESCE(c.contract_status, 0) AS status,
            COALESCE(c.deposit_ymd, '') AS billing_day,
            COALESCE(c.electric_meter_start, 0) AS elec,
            COALESCE(c.water_meter_start, 0) AS water,
            COALESCE(r.base_rent, 0) AS base_rent
        FROM contract c
        LEFT JOIN tenant t 
        ON c.tenant_id = t.tenant_id
        LEFT JOIN room r
        ON r.room_no = c.room_no
        """
        params: tuple = ()
        kw = (keyword or "").strip()
        if kw:
            sql += """
            WHERE c.contract_id LIKE ? OR t.full_name LIKE ?
            """
            pat = f"%{kw}%"
            params = (pat, pat, pat)

        sql += " ORDER BY c.contract_id DESC"

        cur = self.conn.execute(sql, params) if params else self.conn.execute(sql)
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return rows

    def get(self, bill_id: int) -> ContractDTO:
        cur = self.conn.execute("SELECT * FROM contract WHERE contract_id = ?", (bill_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Không tìm thấy contract")
        return self._row_to_dto(row)

    def create(
            self,
            room_no: int,
            tenant_id: int,
            start_ymd: str,
            deposit_amount: int,
            electric_meter_start: int,
            water_meter_start: int,
            contract_name: str,
            end_ymd: str | None = None,
            contract_status: int = 1,
            deposit_ymd: str | None = None,
            electric_meter_ymd: int | None = None,
            note: str | None = None,
    ) -> int:
        cur = self.conn.cursor()

        # (optional) check FK có tồn tại không cho đẹp
        cur.execute("SELECT 1 FROM room WHERE room_no = ? AND is_deleted = 0", (room_no,))
        if cur.fetchone() is None:
            raise ValueError("Room không tồn tại hoặc đã bị xóa")

        cur.execute("SELECT 1 FROM tenant WHERE tenant_id = ? AND is_deleted = 0", (tenant_id,))
        if cur.fetchone() is None:
            raise ValueError("Tenant không tồn tại hoặc đã bị xóa")

        cur.execute(
            """
            INSERT INTO contract (
                room_no,
                tenant_id,
                start_ymd,
                end_ymd,
                deposit_amount,
                electric_meter_start,
                water_meter_start,
                contract_name,
                contract_status,
                deposit_ymd,
                electric_meter_ymd,
                note,
                is_deleted
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                room_no,
                tenant_id,
                start_ymd,
                end_ymd,
                deposit_amount,
                electric_meter_start,
                water_meter_start,
                contract_name,
                contract_status,
                deposit_ymd,
                electric_meter_ymd,
                note,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def _sanitize_filename_part(self, s: str) -> str:
        """Loại bỏ ký tự không an toàn, thay space bằng underscore, trim"""
        if s is None:
            return "unknown"
        s = str(s).strip()
        # thay khoảng trắng bằng _
        s = re.sub(r"\s+", "_", s)
        # giữ lại chữ, số, underscore, dấu -, .
        s = re.sub(r"[^A-Za-z0-9_\-\.]", "", s)
        return s or "unknown"

    def export_contract_pdf(self, contract_id: str, month: str) -> str:
        """
        Xuất PDF cho hợp đồng contract_id, lưu filename dạng:
        Contract_<tenantname>_<YYYYMM>.pdf
        Trả về đường dẫn file (string).
        """
        # --- validate month YYYYMM ---
        if not re.fullmatch(r"\d{6}", str(month or "")):
            raise ValueError("Tháng phải dạng YYYYMM")

        # --- lấy contract ---
        cur = self.conn.execute("SELECT * FROM contract WHERE contract_id = ?", (contract_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Không tìm thấy contract")

        contract = dict(row)

        # --- lấy tenant name (giả sử có table tenant with tenant_id, tenant_name) ---
        tenant_name = "unknown"
        try:
            tcur = self.conn.execute("SELECT tenant_name FROM tenant WHERE tenant_id = ?", (contract["tenant_id"],))
            trow = tcur.fetchone()
            if trow:
                tenant_name = trow["tenant_name"]
        except Exception:
            # nếu không có table/field phù hợp, fallback sang contract.contract_name
            tenant_name = contract.get("contract_name") or tenant_name

        safe_tenant = self._sanitize_filename_part(tenant_name)
        safe_month = str(month)

        filename = f"Contract_{safe_tenant}_{safe_month}.pdf"
        out_path = self._export_dir / filename

        # --- tạo PDF đơn giản bằng ReportLab ---
        try:
            c = canvas.Canvas(str(out_path), pagesize=A4)
            width, height = A4

            left_margin = 40
            y = height - 60

            c.setFont("Helvetica-Bold", 16)
            c.drawString(left_margin, y, "Contract")
            y -= 30

            c.setFont("Helvetica", 11)
            lines = [
                f"Contract ID: {contract.get('contract_id')}",
                f"Contract Name: {contract.get('contract_name')}",
                f"Tenant ID: {contract.get('tenant_id')}",
                f"Tenant Name: {tenant_name}",
                f"Room ID: {contract.get('room_no')}",
                f"Start Date: {contract.get('start_ymd')}",
                f"End Date: {contract.get('end_ymd') or ''}",
                f"Deposit Amount: {contract.get('deposit_amount')}",
                f"Electric Meter Start: {contract.get('electric_meter_start')}",
                f"Water Meter Start: {contract.get('water_meter_start')}",
                f"Deposit Date: {contract.get('deposit_ymd') or ''}",
                f"Status: {contract.get('contract_status')}",
                f"Note: {contract.get('note') or ''}",
                f"Export Month: {safe_month}",
            ]

            for ln in lines:
                c.drawString(left_margin, y, ln)
                y -= 18
                if y < 80:
                    c.showPage()
                    y = height - 60
                    c.setFont("Helvetica", 11)

            c.showPage()
            c.save()
        except Exception as e:
            raise RuntimeError(f"Không thể tạo PDF: {e}")

        return str(out_path)