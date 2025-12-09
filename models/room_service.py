from database.db import get_db

# --- LIST ---
def get_all_rooms():
    conn = get_db()
    return conn.execute(
        """
      SELECT  
      room_id, 
      room_name, 
      base_rent,
      area_m2, 
      floor, 
      electric_unit_price, 
      water_unit_price,
      status, 
      note, 
      FROM room
      WHERE is_deleted = 0
    ORDER BY room_id
    """
    ).fetchall()

# --- GET = room_id
def get_room_by_id (room_id :int):
    conn = get_db()
    return conn.execute("select * from room where room_id = ?", (room_id,)).fetchone()

# --- CREATE ---

def create_room(
        conn.get_db()
conn.execute{
        """
    INSERT
    INTO
    room(
        room_no,
        area_m2,
        floor,
        base_rent,
        electric_unit_price,
        water_unit_price,
        status,
        note,
        is_deleted
    )
    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
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
conn.commit()


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
    FROM
    room
    WHERE
    room_no = ?
    AND
    is_deleted = 0
    """, (room_no,))
row = cur.fetchone()
if row is None:
raise ValueError("This room is not available")

status = 1 if is_active else 0  # 1 = active, 0 = inactive

self.conn.execute("""
    UPDATE
    room
    SET
    area_m2 = ?,
    floor = ?,
    base_rent = ?,
    electric_unit_price = ?,
    water_unit_price = ?,
    status = ?,
    note = ?
    WHERE
    room_no = ?
    AND
    is_deleted = 0
    """, (
        area_m2,
        floor,
        base_rent,
        electric_unit_price,
        water_unit_price,
        status,
        note,
        room_no

    ))
self.conn.commit()


def delete(self, room_no: str) -> None:
if self._room_has_active_tenant(room_no):
raise ValueError("This room is using")

self.conn.execute(
"UPDATE room SET is_deleted = 1 WHERE room_no = ?",
(room_no,)
)
self.conn.commit()
