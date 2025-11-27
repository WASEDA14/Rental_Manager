# contract_model.py
from dataclasses import dataclass
import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
from database.db import get_connection


@dataclass
class ContractDTO:
     contract_id: str
     room_id: int
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
                room_id = d["room_id"],
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

    def list(self, keyword: str | None = None) -> List[ContractDTO]:
        sql = "SELECT * FROM contract WHERE contract_id = ?"
        params: list = []

        sql += " ORDER BY bill_id DESC"
        cur = self.conn.execute(sql, params)
        return [self._row_to_dto(r) for r in cur.fetchall()]

    def get(self, bill_id: int) -> ContractDTO:
        cur = self.conn.execute("SELECT * FROM contract WHERE contract_id = ?", (bill_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Không tìm thấy contract")
        return self._row_to_dto(row)

    def create(
            self,
            room_id: int,
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
        cur.execute("SELECT 1 FROM room WHERE room_id = ? AND is_deleted = 0", (room_id,))
        if cur.fetchone() is None:
            raise ValueError("Room không tồn tại hoặc đã bị xóa")

        cur.execute("SELECT 1 FROM tenant WHERE tenant_id = ? AND is_deleted = 0", (tenant_id,))
        if cur.fetchone() is None:
            raise ValueError("Tenant không tồn tại hoặc đã bị xóa")

        cur.execute(
            """
            INSERT INTO contract (
                room_id,
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
                room_id,
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