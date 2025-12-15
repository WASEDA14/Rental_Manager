from database.db import get_db
# from utils.formatter import format_currency


# --- LIST ---
def get_all_rooms():
    with get_db() as conn:
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
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM room WHERE room_id = ? AND is_deleted = 0",
            (room_id,),
        ).fetchone()

# --- CREATE ---

def get_available_rooms():
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM room WHERE status = 'available' AND is_deleted = 0"
        ).fetchall()


def create_room(data: dict):
    with get_db() as conn:
        required_keys = (
            "room_name",
            "area_m2",
            "floor",
            "base_rent",
            "electric_unit_price",
            "water_unit_price",
            "status",
            "note",
        )
        for k in required_keys:
            if k not in data:
                raise ValueError("Thiếu dữ liệu phòng!")

        exists = conn.execute(
            "SELECT 1 FROM room WHERE UPPER(room_name) = UPPER(?) AND is_deleted = 0",
            (data["room_name"],),
        ).fetchone()
        if exists:
            raise ValueError(f"Phòng '{data['room_name']}' đã tồn tại!")

        cur = conn.execute(
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
        return cur.lastrowid


def update_room(room_id: int, data: dict):
    with get_db() as conn:
        required_keys = (
            "room_name",
            "area_m2",
            "floor",
            "base_rent",
            "electric_unit_price",
            "water_unit_price",
            "status",
            "note",
        )
        for k in required_keys:
            if k not in data:
                raise ValueError("Thiếu dữ liệu phòng!")

        room_exists = conn.execute(
            "SELECT 1 FROM room WHERE room_id = ? AND is_deleted = 0",
            (room_id,),
        ).fetchone()
        if not room_exists:
            raise ValueError("Phòng không tồn tại hoặc đã bị xóa!")

        dup = conn.execute(
            """
            SELECT 1
            FROM room
            WHERE UPPER(room_name) = UPPER(?)
              AND room_id <> ?
              AND is_deleted = 0
            """,
            (data["room_name"], room_id),
        ).fetchone()
        if dup:
            raise ValueError("Tên phòng này đang được sử dụng bởi phòng khác!")

        cur = conn.execute(
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
            WHERE room_id = ? AND is_deleted = 0
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
        if getattr(cur, "rowcount", 1) == 0:
            raise ValueError("Cập nhật thất bại!")


def delete_room(room_id: int):
    with get_db() as conn:
        room_exists = conn.execute(
            "SELECT 1 FROM room WHERE room_id = ? AND is_deleted = 0",
            (room_id,),
        ).fetchone()
        if not room_exists:
            raise ValueError("Phòng không tồn tại hoặc đã bị xóa!")

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

