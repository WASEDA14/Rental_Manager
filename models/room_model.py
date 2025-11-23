from dataclasses import dataclass
from typing import List, Optional
from database.db import get_connection


@dataclass
class RoomDTO:
    room_id: int
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
    def get_by_id(self, room_id: str) -> Optional[RoomDTO]:
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT room_id,
                           room_name,
                           base_rent,
                           area_m2,
                           floor,
                           electric_unit_price,
                           water_unit_price,
                           status,
                           note,
                           is_deleted
                    FROM room
                    WHERE room_id = ?
                      AND is_deleted = 0
                    """, (room_id,))
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
        status = 1 if is_active else 0

        self.conn.execute("""
            INSERT INTO room (
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
        """, (
            room_name,
            None,
            None,
            base_rent,
            electric_unit_price,
            water_unit_price,
            status,
            note,
            0,
        ))
        self.conn.commit()


    # --- UPDATE ---
    def update(
            self,
            room_id: str,
            room_name: str,
            base_rent: int,
            electric_unit_price: int | None,
            water_unit_price: int | None,
            floor: int | None,
            is_active: bool,
            note: str | None,
            area_m2: float | None = None,
    ) -> None:
        # lấy theo room_id, không dùng room_name
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT room_id,
                           room_name,
                           base_rent,
                           area_m2,
                           floor,
                           electric_unit_price,
                           water_unit_price,
                           status,
                           note,
                           is_deleted
                    FROM room
                    WHERE room_id = ?
                      AND is_deleted = 0
                    """, (room_id,))
        row = cur.fetchone()
        if row is None:
            raise ValueError("This room is not available")

        status = 1 if is_active else 0  # 1 = active, 0 = inactive

        self.conn.execute("""
                          UPDATE room
                          SET room_name           = ?,
                              area_m2             = ?,
                              floor               = ?,
                              base_rent           = ?,
                              electric_unit_price = ?,
                              water_unit_price    = ?,
                              status              = ?,
                              note                = ?
                          WHERE room_id = ?
                            AND is_deleted = 0
                          """, (
                              room_name,
                              area_m2,
                              floor,
                              base_rent,
                              electric_unit_price,
                              water_unit_price,
                              status,
                              note,
                              room_id,  # điều kiện WHERE
                          ))
        self.conn.commit()


    def delete(self, room_id: str) -> None:
        self.conn.execute(
            "UPDATE room SET is_deleted = 1 WHERE room_id = ?",
            (room_id,)
        )
        self.conn.commit()




