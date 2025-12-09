import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from database.db import get_connection


@dataclass
class RoomDTO:
    room_no: str
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
        self.conn.row_factory = sqlite3.Row


    # --- LIST ---
    def list(self, keyword: str | None = None) -> List[RoomDTO]:
        cur = self.conn.cursor()

        sql = """
            SELECT  room_no base_rent,
                   area_m2, floor, electric_unit_price, water_unit_price,
                   status, note, is_deleted
            FROM room
            WHERE is_deleted = 0
        """
        params: list = []

        if keyword:
            sql += " AND (CAST(room_no AS TEXT) LIKE ? OR room_no LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw])

        sql += " ORDER BY room_no"

        cur.execute(sql, params)
        rows = cur.fetchall()
        return [RoomDTO(*row) for row in rows]

    # --- GET nội bộ ---
    def get_by_id(self, room_no: str) -> Optional[RoomDTO]:
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT 
                           room_no,
                           base_rent,
                           area_m2,
                           floor,
                           electric_unit_price,
                           water_unit_price,
                           status,
                           note,
                           is_deleted
                    FROM room
                    WHERE room_no = ?
                      AND is_deleted = 0
                    """, (room_no,))
        row = cur.fetchone()
        return RoomDTO(*row) if row else None

    # --- CREATE ---

    def create(
        self,
        room_no: str,
        base_rent: int,
        electric_unit_price: int | None = None,
        water_unit_price: int | None = None,
        note: str | None = None,
        is_active: bool = True,
    ):
        status = 1 if is_active else 0

        self.conn.execute("""
            INSERT INTO room (
                room_no,
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
            room_no,
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
            room_no: str,
            base_rent: int,
            electric_unit_price: int | None,
            water_unit_price: int | None,
            floor: int | None,
            is_active: bool,
            note: str | None,
            area_m2: float | None = None,
    ) -> None:
        cur = self.conn.cursor()
        cur.execute("""
                    SELECT 
                           room_no,
                           base_rent,
                           area_m2,
                           floor,
                           electric_unit_price,
                           water_unit_price,
                           status,
                           note,
                           is_deleted
                    FROM room
                    WHERE room_no = ?
                      AND is_deleted = 0
                    """, (room_no,))
        row = cur.fetchone()
        if row is None:
            raise ValueError("This room is not available")

        status = 1 if is_active else 0  # 1 = active, 0 = inactive

        self.conn.execute("""
                          UPDATE room
                          SET 
                              area_m2             = ?,
                              floor               = ?,
                              base_rent           = ?,
                              electric_unit_price = ?,
                              water_unit_price    = ?,
                              status              = ?,
                              note                = ?
                          WHERE room_no = ?
                            AND is_deleted = 0
                          """, (
                              room_no,
                              area_m2,
                              floor,
                              base_rent,
                              electric_unit_price,
                              water_unit_price,
                              status,
                              note,

                          ))
        self.conn.commit()


    def delete(self, room_no: str) -> None:
        self.conn.execute(
            "UPDATE room SET is_deleted = 1 WHERE room_no = ?",
            (room_no,)
        )
        self.conn.commit()




