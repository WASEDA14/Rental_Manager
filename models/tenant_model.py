import sqlite3
from typing import Optional, List
from dataclasses import dataclass
from datetime import date, datetime

from database.db import get_connection


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
    if not s:
        return None
    return datetime.strptime(s, "%Y-%m-%d").date()


def _date_to_str(d: Optional[date]) -> Optional[str]:
    if not d:
        return None
    return d.strftime("%Y-%m-%d")


def _phone_ok(p: str | None) -> bool:
    return (p is None) or (p.isdigit() and 9 <= len(p) <= 11)


class TenantModel:
    def __init__(self):
        self.conn = get_connection()
        self.conn.row_factory = sqlite3.Row

    # ---------- internal mapping ----------
    def _row_to_dto(self, row: sqlite3.Row) -> TenantDTO:
        d = dict(row)
        return TenantDTO(
            id=d["tenant_id"],
            name=d["name"],
            phone=d["phone"],
            room_code=d["room_code"],
            move_in=_parse_date(d["move_in"]),
            move_out=_parse_date(d["move_out"]),
            email=d["email"],
            id_no=d["id_no"],
            active=bool(d["active"]),
        )

    # ---------- helpers ----------
    def _room_exists(self, room_code: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM room WHERE room_code = ? AND is_deleted = 0",
            (room_code,),
        )
        return cur.fetchone() is not None

    def _room_has_active_tenant(self, room_code: str, exclude_id: int | None = None) -> bool:
        sql = "SELECT 1 FROM tenant WHERE room_code = ? AND active = 1"
        params: list = [room_code]
        if exclude_id is not None:
            sql += " AND id <> ?"
            params.append(exclude_id)
        cur = self.conn.execute(sql, params)
        return cur.fetchone() is not None

    # ---------- Query ----------
    def list(self, keyword: str | None = None) -> List[TenantDTO]:
        sql = "SELECT * FROM tenant"
        params: list = []
        if keyword:
            sql += " WHERE name LIKE ? OR phone LIKE ? OR room_code LIKE ?"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])
        sql += " ORDER BY tenant_id DESC"
        cur = self.conn.execute(sql, params)
        return [self._row_to_dto(r) for r in cur.fetchall()]

    def get(self, tenant_id: int) -> TenantDTO:
        cur = self.conn.execute("SELECT * FROM tenant WHERE tenant_id = ?", (tenant_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Không tìm thấy tenant")
        return self._row_to_dto(row)

    # ---------- Commands ----------
    def create(
        self,
        *,
        name: str,
        phone: str | None,
        room_code: str,
        move_in: str | None = None,
        move_out: str | None = None,
        email: str | None = None,
        id_no: str | None = None,
    ) -> TenantDTO:

        name = name.strip()
        if len(name) < 2:
            raise ValueError("Tên phải ≥ 2 ký tự")
        if not _phone_ok(phone):
            raise ValueError("SĐT không hợp lệ (9–11 số)")

        room_code = room_code.strip()
        if not self._room_exists(room_code):
            raise ValueError("Phòng không tồn tại")

        # check phòng đã có người ở chưa
        if self._room_has_active_tenant(room_code):
            raise ValueError("Phòng đã có người ở")

        mv_in = _parse_date(move_in)
        mv_out = _parse_date(move_out)
        if mv_in and mv_out and mv_out < mv_in:
            raise ValueError("Ngày ra phải ≥ ngày vào")

        cur = self.conn.execute(
            """
            INSERT INTO tenant
                (name, phone, room_code, move_in, move_out, email, id_no, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                phone,
                room_code,
                _date_to_str(mv_in),
                _date_to_str(mv_out),
                email,
                id_no,
                1,  # active
            ),
        )
        self.conn.commit()
        new_id = cur.lastrowid
        return self.get(new_id)

    def update(self, tenant_id: int, **fields) -> TenantDTO:
        t = self.get(tenant_id)  # lấy DTO hiện tại

        # làm việc trên dict tạm, rồi UPDATE 1 lần
        data = t.__dict__.copy()

        if "name" in fields:
            nm = str(fields["name"]).strip()
            if len(nm) < 2:
                raise ValueError("Tên phải ≥ 2 ký tự")
            data["name"] = nm

        if "phone" in fields:
            ph = fields["phone"]
            if not _phone_ok(ph):
                raise ValueError("SĐT không hợp lệ")
            data["phone"] = ph

        if "room_code" in fields:
            new_room = str(fields["room_code"]).strip()
            if not self._room_exists(new_room):
                raise ValueError("Phòng không tồn tại")
            # nếu đổi phòng, check phòng mới rảnh
            if new_room != t.room_code and self._room_has_active_tenant(new_room, exclude_id=tenant_id):
                raise ValueError("Phòng mới đã có người")
            data["room_code"] = new_room

        if "move_in" in fields:
            data["move_in"] = _parse_date(fields["move_in"])
        if "move_out" in fields:
            mv_out = _parse_date(fields["move_out"])
            if data["move_in"] and mv_out and mv_out < data["move_in"]:
                raise ValueError("Ngày ra phải ≥ ngày vào")
            data["move_out"] = mv_out

        if "email" in fields:
            data["email"] = fields["email"]
        if "id_no" in fields:
            data["id_no"] = fields["id_no"]
        if "active" in fields:
            data["active"] = bool(fields["active"])

        self.conn.execute(
            """
            UPDATE tenant
            SET name = ?, phone = ?, room_code = ?,
                move_in = ?, move_out = ?,
                email = ?, id_no = ?, active = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["phone"],
                data["room_code"],
                _date_to_str(data["move_in"]),
                _date_to_str(data["move_out"]),
                data["email"],
                data["id_no"],
                1 if data["active"] else 0,
                tenant_id,
            ),
        )
        self.conn.commit()
        return self.get(tenant_id)

    def delete(self, tenant_id: int) -> None:
        # hard delete; nếu muốn soft delete thì đổi thành active = 0
        self.conn.execute("DELETE FROM tenant WHERE tenant_id = ?", (tenant_id,))
        self.conn.commit()

    # ---------- Business helpers ----------
    def move_room(self, tenant_id: int, new_room_code: str) -> TenantDTO:
        return self.update(tenant_id, room_code=new_room_code)

    def checkout(self, tenant_id: int, move_out: str) -> TenantDTO:
        return self.update(tenant_id, active=False, move_out=move_out)
