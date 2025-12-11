from database.db import get_db
# from utils.formatter import format_currency


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
      note
      FROM room
      WHERE is_deleted = 0
    ORDER BY room_id
    """
    ).fetchall()

# --- GET = room_id
def get_room_by_id (room_id :int):
    conn = get_db()
    return conn.execute("SELECT * FROM room WHERE room_id = ?", (room_id,)).fetchone()

# --- CREATE ---

def get_available_rooms():
    conn = get_db()
    return conn.execute(
        "SELECT * FROM room WHERE status = 'available' AND is_deleted = 0"
    ).fetchall()


def create_room(data: dict):
    conn = get_db()
    conn.execute(
        """
                 INSERT INTO room (
                     room_name,
                     area_m2, floor, base_rent, electric_unit_price,
                     water_unit_price, status, note
                 )
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                 """,
        (
            data["room_name"],
            data["area_m2"],
            data["floor"],
            data["base_rent"],
            data["electric_unit_price"],
            data["water_unit_price"],
            data["status"],
            data["note"],
        ),
    )
    conn.commit()




def update_room(room_id: int, data: dict):
    conn = get_db()
    conn.execute(
        """
                 UPDATE room
                 SET room_name = ?,
                     area_m2 = ?,
                     floor = ?,
                     base_rent = ?,
                     electric_unit_price = ?,
                     water_unit_price = ?,
                     status = ?,
                     note = ?
                 WHERE room_id = ?
                 """,
        (
            data["room_name"],
            data["area_m2"],
            data["floor"],
            data["base_rent"],
            data["electric_unit_price"],
            data["water_unit_price"],
            data["status"],
            data["note"],
            room_id,
        ),
    )
    conn.commit()


def delete_room(room_id: int):
    conn = get_db()
    active_contract = conn.execute(
        """
            SELECT 1 FROM contract
            WHERE room_id = ? AND contract_status = 'active' AND is_deleted = 0
             """,
        (room_id,),
    ).fetchone()

    if active_contract:
        raise ValueError("Không thể xóa phòng đang có hợp đồng hiệu lực!")

    conn.execute("UPDATE room SET is_deleted = 1 WHERE room_id = ?", (room_id,))
    conn.commit()




def get_available_rooms():
    conn = get_db()
    return conn.execute(
        "SELECT * FROM room WHERE status = 'available' AND is_deleted = 0"
    ).fetchall()