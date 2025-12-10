from database.db import get_db
from datetime import datetime

def get_all_bills():
    conn = get_db()
    return conn.execute(
        """
        SELECT b.*, r.name_room, t.full_name, c.rent as contract_rent
        FROM bill b
        JOIN contract c ON b.contract_id = c.contract_id
        JOIN room r ON c.room_id = r.room_id
        JOIN tenant t ON c.tenant_id = t.tenant_id
        WHERE b.is_deleted = 0
        ORDER BY b.bill_id DESC
    """
    ).fetchall()


def get_active_contracts_with_last_bill():
    conn = get_db()
    return conn.execute(
        """
        SELECT 
            c.contract_id,
            r.name_room,
            t.full_name,
            c.rent,
            r.electric_unit_price,
            r.water_unit_price,
            c.electric_meter_start,
            c.water_meter_start,
            COALESCE(lb.elec_current, c.electric_meter_start, 0) as elec_prev,
            COALESCE(lb.water_current, c.water_meter_start, 0) as water_prev,
            lb.bill_month as last_bill_month
        FROM contract c
        JOIN room r ON c.room_id = r.room_id
        JOIN tenant t ON c.tenant_id = t.tenant_id
        LEFT JOIN (
            SELECT contract_id, elec_current, water_current, bill_month,
                   ROW_NUMBER() OVER (PARTITION BY contract_id ORDER BY bill_month DESC) as rn
            FROM bill WHERE is_deleted = 0
        ) lb ON c.contract_id = lb.contract_id AND lb.rn = 1
        WHERE c.contract_status = 'active' AND c.is_deleted = 0
        ORDER BY r.name_room
    """
    ).fetchall()


def get_next_bill_month(contract_id: int) -> str:
    conn = get_db()
    row = conn.execute(
        """
        SELECT bill_month FROM bill 
        WHERE contract_id = ? AND is_deleted = 0
        ORDER BY bill_month DESC LIMIT 1
    """,
        (contract_id,),
    ).fetchone()

    if not row:
        today = datetime.today()
        return today.strftime("%m/%Y")

    last_month_str = row[0]
    month, year = map(int, last_month_str.split("/"))
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1
    return f"{next_month:02d}/{next_year}"


def bill_exists(contract_id: int, bill_month: str) -> bool:
    conn = get_db()
    row = conn.execute(
        """
        SELECT 1 FROM bill WHERE contract_id = ? AND bill_month = ? AND is_deleted = 0
    """,
        (contract_id, bill_month),
    ).fetchone()
    return row is not None


def create_bill(data: dict):
    conn = get_db()
    total = (
        data["room_rent_amount"]
        + (data["elec_current"] - data["elec_prev"]) * data["electric_unit_price"]
        + (data["water_current"] - data["water_prev"]) * data["water_unit_price"]
        + data.get("other_fee", 0)
    )

    conn.execute(
        """
        INSERT INTO bill (
            bill_code, contract_id, bill_month,
            elec_prev, elec_current, water_prev, water_current,
            electric_unit_price, water_unit_price,
            room_rent_amount, other_fee, total_amount, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data["bill_code"],
            data["contract_id"],
            data["bill_month"],
            data["elec_prev"],
            data["elec_current"],
            data["water_prev"],
            data["water_current"],
            data["electric_unit_price"],
            data["water_unit_price"],
            data["room_rent_amount"],
            data.get("other_fee", 0),
            total,
            data.get("note"),
        ),
    )
    conn.commit()


def update_bill(bill_id: int, data: dict):
    conn = get_db()
    total = (
        data["room_rent_amount"]
        + (data["elec_current"] - data["elec_prev"]) * data["electric_unit_price"]
        + (data["water_current"] - data["water_prev"]) * data["water_unit_price"]
        + data.get("other_fee", 0)
    )

    conn.execute(
        """
        UPDATE bill SET
            bill_month=?, elec_prev=?, elec_current=?, water_prev=?, water_current=?,
            electric_unit_price=?, water_unit_price=?, room_rent_amount=?,
            other_fee=?, total_amount=?, note=?
        WHERE bill_id=?
    """,
        (
            data["bill_month"],
            data["elec_prev"],
            data["elec_current"],
            data["water_prev"],
            data["water_current"],
            data["electric_unit_price"],
            data["water_unit_price"],
            data["room_rent_amount"],
            data.get("other_fee", 0),
            total,
            data.get("note"),
            bill_id,
        ),
    )
    conn.commit()



def delete_bill(bill_id: int):
    conn = get_db()
    conn.execute("UPDATE bill SET is_deleted = 1 WHERE bill_id = ?", (bill_id,))
    conn.commit()


def mark_bill_paid(bill_id: int):
    conn = get_db()
    conn.execute(
        """
        UPDATE bill SET 
            paid_status = 'paid', 
            paid_amount = total_amount, 
            paid_ymd = date('now')
        WHERE bill_id = ?
    """,
        (bill_id,),
    )
    conn.commit()