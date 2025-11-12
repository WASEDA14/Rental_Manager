# services/tenant_service.py
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Callable

# callback để lấy danh sách phòng hợp lệ (vd: từ RoomService)
# dạng: get_rooms() -> List[str]  (trả về list room_code, ví dụ ["R101","R102"])
GetRoomsFn = Callable[[], List[str]]

@dataclass
class TenantDTO:
    id: int | None
    name: str
    phone: str | None
    room_code: str
    move_in: Optional[date] = None
    move_out: Optional[date] = None
    email: Optional[str] = None
    id_no: Optional[str] = None
    active: bool = True

def _parse_date(s: str | None) -> Optional[date]:
    if not s: return None
    return datetime.strptime(s, "%Y-%m-%d").date()

def _phone_ok(p: str | None) -> bool:
    return (p is None) or (p.isdigit() and 9 <= len(p) <= 11)

class TenantService:
    """
    Service mỏng: quản lý danh sách tenant trong bộ nhớ.
    UI gọi thẳng các hàm dưới đây. Sau này thay bằng bản dùng DB nhưng giữ nguyên chữ ký.
    """
    def __init__(self, get_rooms: GetRoomsFn | None = None):
        self._data: list[TenantDTO] = []
        self._auto = 1
        self._get_rooms = get_rooms or (lambda: [])  # có thể bỏ qua nếu chưa cần check phòng

    # ---------- Query ----------
    def list(self, keyword: str | None = None) -> list[TenantDTO]:
        if not keyword:
            return list(self._data)
        kw = keyword.lower()
        return [t for t in self._data
                if kw in t.name.lower() or (t.phone and kw in t.phone) or kw in t.room_code.lower()]

    def counts(self) -> tuple[int, int]:
        """return (active, total)"""
        total = len(self._data)
        active = sum(1 for t in self._data if t.active)
        return active, total

    # ---------- Commands ----------
    def create(self, *, name: str, phone: str | None, room_code: str,
               move_in: str | None = None, email: str | None = None,
               id_no: str | None = None) -> TenantDTO:
        name = name.strip()
        if len(name) < 2:
            raise ValueError("Tên phải ≥ 2 ký tự")
        if not _phone_ok(phone):
            raise ValueError("SĐT không hợp lệ (9–11 số)")
        if self._get_rooms() and room_code not in self._get_rooms():
            raise ValueError("Phòng không tồn tại")
        # Rule mẫu: 1 phòng chỉ 1 tenant đang active
        if any(t.room_code == room_code and t.active for t in self._data):
            raise ValueError("Phòng đã có người ở")

        dto = TenantDTO(
            id=self._auto, name=name, phone=phone, room_code=room_code,
            move_in=_parse_date(move_in), email=email, id_no=id_no, active=True
        )
        self._auto += 1
        self._data.append(dto)
        return dto

    def update(self, tenant_id: int, **fields) -> TenantDTO:
        t = self._get(tenant_id)
        if "name" in fields:
            nm = str(fields["name"]).strip()
            if len(nm) < 2: raise ValueError("Tên phải ≥ 2 ký tự")
            t.name = nm
        if "phone" in fields:
            ph = fields["phone"]
            if not _phone_ok(ph): raise ValueError("SĐT không hợp lệ")
            t.phone = ph
        if "room_code" in fields:
            new_room = fields["room_code"]
            if self._get_rooms() and new_room not in self._get_rooms():
                raise ValueError("Phòng không tồn tại")
            # nếu đổi phòng, check phòng mới rảnh
            if new_room != t.room_code and any(x.room_code == new_room and x.active for x in self._data):
                raise ValueError("Phòng mới đã có người")
            t.room_code = new_room
        if "move_in" in fields:
            t.move_in = _parse_date(fields["move_in"])
        if "move_out" in fields:
            mv_out = _parse_date(fields["move_out"])
            if t.move_in and mv_out and mv_out < t.move_in:
                raise ValueError("Ngày ra phải ≥ ngày vào")
            t.move_out = mv_out
        if "email" in fields: t.email = fields["email"]
        if "id_no" in fields: t.id_no = fields["id_no"]
        if "active" in fields: t.active = bool(fields["active"])
        return t

    def delete(self, tenant_id: int) -> None:
        self._data = [x for x in self._data if x.id != tenant_id]

    # ---------- Business helpers ----------
    def move_room(self, tenant_id: int, new_room_code: str) -> TenantDTO:
        return self.update(tenant_id, room_code=new_room_code)

    def checkout(self, tenant_id: int, move_out: str) -> TenantDTO:
        return self.update(tenant_id, active=False, move_out=move_out)

    # ---------- internal ----------
    def _get(self, tenant_id: int) -> TenantDTO:
        for t in self._data:
            if t.id == tenant_id:
                return t
        raise ValueError("Không tìm thấy tenant")
