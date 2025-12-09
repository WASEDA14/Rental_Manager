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
    room_no: str
    move_in: Optional[date] = None
    move_out: Optional[date] = None
    email: Optional[str] = None
    id_number: Optional[str] = None
    is_deleted: bool = True


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
            name=d["full_name"],
            phone=d["phone"],
            room_no=d["room_no"],
            move_in=_parse_date(d["move_in"]),
            move_out=_parse_date(d["move_out"]),
            email=d["email"],
            id_number=d["id_number"],
            is_deleted=bool(d["is_deleted"]),
        )

    # ---------- helpers ----------
    def _room_exists(self, room_no: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM room WHERE room_no = ? AND is_deleted = 0",
            (room_no,),
        )
        return cur.fetchone() is not None

    def _room_has_active_tenant(self, room_no: str, exclude_id: int | None = None) -> bool:
        sql = """
            SELECT 1
            FROM tenant
            WHERE room_no = ?
              AND is_deleted = 0
        """
        params: list = [room_no]

        if exclude_id is not None:
            sql += " AND tenant_id <> ?"
            params.append(exclude_id)

        sql += " LIMIT 1"

        cur = self.conn.execute(sql, params)
        return cur.fetchone() is not None

    # ---------- Query ----------
    def list(self, keyword: str | None = None) -> List[TenantDTO]:
        sql = "SELECT * FROM tenant"
        params: list = []
        if keyword:
            sql += " WHERE full_name LIKE ? OR phone LIKE ? OR room_no LIKE ?"
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
        full_name: str,
        phone: str | None,
        room_no: str,
        move_in: str | None = None,
        move_out: str | None = None,
        email: str | None = None,
        id_number: str | None = None,
        is_deleted: int = 0
    ) -> TenantDTO:

        full_name = full_name.strip()
        if len(full_name) < 2:
            raise ValueError("Tên phải ≥ 2 ký tự")
        if not _phone_ok(phone):
            raise ValueError("SĐT không hợp lệ (9–11 số)")

        room_no = room_no.strip()
        if not self._room_exists(room_no):
            raise ValueError("Phòng không tồn tại")

        # check phòng đã có người ở chưa
        if self._room_has_active_tenant(room_no):
            raise ValueError("Phòng đã có người ở")

        mv_in = _parse_date(move_in)
        mv_out = _parse_date(move_out)
        if mv_in and mv_out and mv_out < mv_in:
            raise ValueError("Ngày ra phải ≥ ngày vào")

        cur = self.conn.execute(
            """
            INSERT INTO tenant
                (full_name, phone, room_no, move_in, move_out, email,id_number, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, ?,?)
            """,
            (
                full_name,
                phone,
                room_no,
                _date_to_str(mv_in),
                _date_to_str(mv_out),
                email,
                id_number,
                is_deleted,             ),
        )
        self.conn.commit()
        new_id = cur.lastrowid
        return self.get(new_id)

    def update(self, tenant_id: int, **fields) -> TenantDTO:
        t = self.get(tenant_id)  # lấy DTO hiện tại

        # làm việc trên dict tạm, rồi UPDATE 1 lần
        data = t.__dict__.copy()

        if "full_name" in fields:
            nm = str(fields["full_name"]).strip()
            if len(nm) < 2:
                raise ValueError("Tên phải ≥ 2 ký tự")
            data["full_name"] = nm

        if "phone" in fields:
            ph = fields["phone"]
            if not _phone_ok(ph):
                raise ValueError("SĐT không hợp lệ")
            data["phone"] = ph

        if "room_no" in fields:
            new_room = str(fields["room_no"]).strip()
            if not self._room_exists(new_room):
                raise ValueError("Phòng không tồn tại")
            # nếu đổi phòng, check phòng mới rảnh
            if new_room != t.room_no and self._room_has_active_tenant(new_room, exclude_id=tenant_id):
                raise ValueError("Phòng mới đã có người")
            data["room_no"] = new_room

        if "move_in" in fields:
            data["move_in"] = _parse_date(fields["move_in"])
        if "move_out" in fields:
            mv_out = _parse_date(fields["move_out"])
            if data["move_in"] and mv_out and mv_out < data["move_in"]:
                raise ValueError("Ngày ra phải ≥ ngày vào")
            data["move_out"] = mv_out

        if "email" in fields:
            data["email"] = fields["email"]
        if "id_number" in fields:
            data["id_number"] = fields["id_number"]
        if "active" in fields:
            data["active"] = bool(fields["is_deleted"])

        is_deleted = 0 if data["active"] else 1

        self.conn.execute(
            """
            UPDATE tenant
            SET full_name = ?, phone = ?, room_no = ?,
                move_in = ?, move_out = ?,
                email = ?,id_number = ?, is_deleted = ?
            WHERE id = ?
            """,
            (
                data["full_name"],
                data["phone"],
                data["room_no"],
                _date_to_str(data["move_in"]),
                _date_to_str(data["move_out"]),
                data["email"],
                data["id_number"],
                is_deleted,
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
    def move_room(self, tenant_id: int, new_room_no: str) -> TenantDTO:
        return self.update(tenant_id, room_no=new_room_no)

    def checkout(self, tenant_id: int, move_out: str) -> TenantDTO:
        return self.update(tenant_id, active=False, move_out=move_out)
