from dataclasses import dataclass
from typing import List, Optional
from database.db import get_connection


@dataclass
class RoomDTO:
    room_id: int              # TEXT trong DB
    room_name: str
    base_rent: int
    area_m2: Optional[float] = None
    floor: Optional[int] = None
    electric_unit_price: Optional[int] = None
    water_unit_price: Optional[int] = None
    status: int = 1
    note: Optional[str] = None
    is_deleted: int = 0


class RoomModel:
    def __init__(self):
        self.conn = get_connection()

    # --- LIST ---
    def list(self, keyword: str | None = None) -> List[RoomDTO]:
        cur = self.conn.cursor()

        sql = """
            SELECT room_id, room_name, base_rent,
                   area_m2, floor, electric_unit_price, water_unit_price,
                   status, note, is_deleted
            FROM room
            WHERE is_deleted = 0
        """
        params: list = []

        if keyword:
            sql += " AND (room_id LIKE ? OR room_name LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw])

        sql += " ORDER BY room_id"

        cur.execute(sql, params)
        rows = cur.fetchall()
        return [RoomDTO(*row) for row in rows]

    # --- GET nội bộ ---
    def get(self, room_name: str) -> Optional[RoomDTO]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT room_id, room_name, base_rent,
                   area_m2, floor, electric_unit_price, water_unit_price,
                   status, note, is_deleted
            FROM room
            WHERE room_name = ? AND is_deleted = 0
        """, (room_name,))
        row = cur.fetchone()
        return RoomDTO(*row) if row else None

    # --- CREATE ---

    def create(
        self,
        room_name: str,
        base_rent: int,
        electric_unit_price: int | None = None,
        water_unit_price: int | None = None,
        note: str | None = None,
        is_active: bool = True,
    ):
        # check trùng
        if self.get(room_name) is not None:
            raise ValueError(f"Room ID '{room_name}' đã tồn tại.")

        status = 1 if is_active else 0

        self.conn.execute("""
            INSERT INTO room (
                /*room_id,*/ 
                room_name, 
                area_m2, 
                floor,
                base_rent, 
                electric_unit_price, 
                water_unit_price,
                status, 
                note, 
               is_deleted
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                          """,
(
            # code,      # room_id
            room_name,      # room_name
            None,      # area_m2
            None,      # floor
            base_rent, # base_rent
            electric_unit_price,         # electric_unit_price
            water_unit_price,         # water_unit_price
            1 if is_active else 0,
            note,      # note
            0,         # is_deleted
        ))
        self.conn.commit()

    # --- UPDATE ---
    def update(self, room_id: str, code: str, base_rent: int,electric_unit_price : int,water_unit_price: int, floor: int,is_active: bool, note: str,area_m2: float | None = None) -> None:
        existing = self.get(room_id)
        if existing is None:
            raise ValueError("This room is not available")

        status = "AVAILABLE" if is_active else "INACTIVE"

        # Update infor room
        existing.base_rent = base_rent
        existing.electric_unit_price = electric_unit_price
        existing.water_unit_price = water_unit_price
        existing.status = status
        existing.room_name = code
        existing.area_m2= area_m2
        existing.floor = floor
        existing.note = note

        self.conn.execute("""
            UPDATE room
            SET room_name = ?,
                base_rent = ?,
                status = ?
            WHERE room_id = ? AND is_deleted = 0
        """, (
            existing.room_name,
            existing.base_rent,
            existing.status,
            existing.room_id
        ))
        self.conn.commit()


    def delete(self, room_id: str) -> None:
        self.conn.execute(
            "UPDATE room SET is_deleted = 1 WHERE room_id = ?",
            (room_id,)
        )
        self.conn.commit()
