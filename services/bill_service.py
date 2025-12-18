import os
import tempfile
from datetime import datetime
from pathlib import Path

from database.db import get_db
from utils.pdf_utils import create_bill_pdf, create_contract_pdf

def get_all_bills():
    with get_db() as conn:
        return conn.execute(
            """
            SELECT b.*, r.room_name, t.full_name, c.rent as contract_rent
            FROM bill b
            JOIN contract c ON b.contract_id = c.contract_id
            JOIN room r ON c.room_id = r.room_id
            JOIN tenant t ON c.tenant_id = t.tenant_id
            WHERE b.is_deleted = 0
            ORDER BY b.bill_id DESC
            """
        ).fetchall()


def get_active_contracts_with_last_bill():
    with get_db() as conn:
        return conn.execute(
            """
            SELECT 
                c.contract_id,
                r.room_name,
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
            ORDER BY r.room_name
            """
        ).fetchall()


def get_next_bill_month(contract_id: int) -> str:
    with get_db() as conn:
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
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT 1 FROM bill WHERE contract_id = ? AND bill_month = ? AND is_deleted = 0
            """,
            (contract_id, bill_month),
        ).fetchone()
        return row is not None


def create_bill(data: dict):
    # Calculate total amount
    total = (
        data["room_rent_amount"]
        + (data["elec_current"] - data["elec_prev"]) * data["electric_unit_price"]
        + (data["water_current"] - data["water_prev"]) * data["water_unit_price"]
        + data.get("other_fee", 0)
    )

    with get_db() as conn:
        # Get tenant_name from contract
        contract_info = conn.execute(
            """
            SELECT t.full_name 
            FROM contract c
            JOIN tenant t ON c.tenant_id = t.tenant_id
            WHERE c.contract_id = ?
            """,
            (data["contract_id"],)
        ).fetchone()

        if not contract_info:
            raise ValueError("Contract not found")

        tenant_name = contract_info[0]

        # Get room_name from contract
        room_info = conn.execute(
            """
            SELECT r.room_name 
            FROM contract c
            JOIN room r ON c.room_id = r.room_id
            WHERE c.contract_id = ?
            """,
            (data["contract_id"],)
        ).fetchone()

        if not room_info:
            raise ValueError("Room not found for this contract")

        room_name = room_info[0]

        # Insert the bill
        conn.execute(
            """
            INSERT INTO bill (
                contract_id, tenant_name, room_id,room_name, bill_month,
                elec_prev, elec_current, water_prev, water_current,
                electric_unit_price, water_unit_price,
                room_rent_amount, other_fee, total_amount, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["contract_id"],
                data["tenant_name"],
                data["room_id"],
                data["room_name"],
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
                data.get("note", ""),
            ),
        )
        conn.commit()


def update_bill(bill_id: int, data: dict):
    total = (
        data["room_rent_amount"]
        + (data["elec_current"] - data["elec_prev"]) * data["electric_unit_price"]
        + (data["water_current"] - data["water_prev"]) * data["water_unit_price"]
        + data.get("other_fee", 0)
    )

    with get_db() as conn:
        conn.execute(
            """
            UPDATE bill SET
                bill_month=?,
                elec_prev=?,
                elec_current=?,
                water_prev=?,
                water_current=?,
                electric_unit_price=?,
                water_unit_price=?,
                room_rent_amount=?,
                other_fee=?,
                total_amount=?,
                note=?
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
    with get_db() as conn:
        conn.execute("UPDATE bill SET is_deleted = 1 WHERE bill_id = ?", (bill_id,))
        conn.commit()


def mark_bill_paid(bill_id: int):
    with get_db() as conn:
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


def get_bill_for_export(bill_id: int) -> dict:
    """Get bill data for PDF export"""
    with get_db() as conn:
        bill = conn.execute(
            """
            SELECT b.*, r.room_name, t.full_name as tenant_name, t.phone, 
                   t.address, c.rent as room_rent_amount
            FROM bill b
            JOIN contract c ON b.contract_id = c.contract_id
            JOIN room r ON c.room_id = r.room_id
            JOIN tenant t ON c.tenant_id = t.tenant_id
            WHERE b.bill_id = ? AND b.is_deleted = 0
            """,
            (bill_id,)
        ).fetchone()
        
        if not bill:
            raise ValueError("Bill not found or has been deleted")
            
        # Convert to dict for easier access
        bill_dict = dict(bill)
        
        # Add additional fields if needed
        bill_dict['bill_code'] = f"HD{bill_id:06d}"
        bill_dict['created_date'] = datetime.now().strftime("%d/%m/%Y")
        
        return bill_dict

PDF_EXPORT_DIR = Path("D:/Rental_Manager/exports/bill")
def export_bill_to_pdf(bill_id: int, output_dir: str = None) -> str:

    bill_data = get_bill_for_export(bill_id)

    output_dir = Path(output_dir) if output_dir else PDF_EXPORT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"HoaDon_{bill_data['bill_code']}_{bill_data['bill_month'].replace('/', '-')}.pdf"
    output_path = output_dir / filename
    
    create_bill_pdf(bill_data, str(output_path))
    return str(output_path)
