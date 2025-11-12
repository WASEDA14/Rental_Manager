# services/bill_service.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class BillDTO:
    id: int | None
    tenant_name: str
    room_code: str
    month: str       # "YYYY-MM"
    total: float
    paid: bool
    created_at: str

class BillService:
    def __init__(self):
        self._data: list[BillDTO] = []
        self._auto = 1

    def list(self, keyword: str | None = None) -> list[BillDTO]:
        if not keyword:
            return list(self._data)
        kw = keyword.lower()
        return [b for b in self._data if kw in b.tenant_name.lower() or kw in b.room_code.lower()]

    def create(self, tenant_name: str, room_code: str, month: str, total: float):
        if not tenant_name.strip():
            raise ValueError("Tên khách trống")
        if not month or len(month) != 7:
            raise ValueError("Tháng phải dạng YYYY-MM")
        dto = BillDTO(
            id=self._auto,
            tenant_name=tenant_name.strip(),
            room_code=room_code.strip(),
            month=month,
            total=float(total),
            paid=False,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        self._auto += 1
        self._data.append(dto)
        return dto

    def update(self, bill_id: int, **fields):
        b = self._get(bill_id)
        if "total" in fields: b.total = float(fields["total"])
        if "paid" in fields: b.paid = bool(fields["paid"])
        return b

    def mark_paid(self, bill_id: int):
        b = self._get(bill_id)
        b.paid = True

    def delete(self, bill_id: int):
        self._data = [x for x in self._data if x.id != bill_id]

    def _get(self, bill_id: int) -> BillDTO:
        for b in self._data:
            if b.id == bill_id:
                return b
        raise ValueError("Không tìm thấy bill")
