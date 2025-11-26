# contract_model.py
import sqlite3
from typing import Optional, List, Dict, Any


class ContractDTO:
    contract_id: str              # TEXT trong DB (có thể dùng AUTOINCREMENT INTEGER PRIMARY KEY cũng được)
    room_id: str                  # FK sang room
    tenant_id: str                # FK sang tenant
    start_date: str               # 'YYYY-MM-DD'
    end_date: Optional[str]       # 'YYYY-MM-DD' hoặc None
    deposit: int                  # tiền cọc
    monthly_rent: int             # tiền thuê hằng tháng (có thể khác base_rent của room)
    status: str                   # ACTIVE / ENDED / CANCELED ...
    note: Optional[str]
    is_deleted: int