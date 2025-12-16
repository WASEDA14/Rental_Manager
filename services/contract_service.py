# services/contract_service.py
import os
from datetime import datetime
from database.db import get_db
from utils.pdf_utils import create_contract_pdf
from config import UPLOAD_FOLDER


def get_all_contracts():
    with get_db() as conn:
        return conn.execute(
            """
            SELECT c.*, r.room_name, t.full_name
            FROM contract c
            JOIN room r ON c.room_id = r.room_id AND r.is_deleted = 0
            JOIN tenant t ON c.tenant_id = t.tenant_id AND t.is_deleted = 0
            WHERE c.is_deleted = 0
            ORDER BY c.contract_id DESC
            """
        ).fetchall()


def get_active_contract_count():
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM contract WHERE contract_status = 'active' AND is_deleted = 0"
        ).fetchone()
        return row[0] if row else 0


def create_contract(data: dict):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO contract (
                room_id, tenant_id, contract_name, start_ymd, end_ymd,
                rent, deposit_amount, electric_meter_start, water_meter_start,
                deposit_ymd, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["room_id"],
                data["tenant_id"],
                data["contract_name"],
                data["start_ymd"],
                data["end_ymd"],
                data["rent"],
                data["deposit_amount"],
                data["electric_meter_start"],
                data["water_meter_start"],
                data["deposit_ymd"],
                data.get("note", ""),
            ),
        )
        conn.execute(
            "UPDATE room SET status = 1 WHERE room_id = ?", (data["room_id"],)
        )
        conn.commit()


def update_contract(contract_id: int, data: dict):
    with get_db() as conn:
        conn.execute(
            """
            UPDATE contract SET
                room_id = ?,
                tenant_id = ?,
                contract_name = ?,
                start_ymd = ?,
                end_ymd = ?,
                rent = ?,
                deposit_amount = ?,
                electric_meter_start = ?,
                water_meter_start = ?,
                deposit_ymd = ?,
                note = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE contract_id = ?
            """,
            (
                data["room_id"],
                data["tenant_id"],
                data["contract_name"],
                data["start_ymd"],
                data["end_ymd"],
                data["rent"],
                data["deposit_amount"],
                data["electric_meter_start"],
                data["water_meter_start"],
                data["deposit_ymd"],
                data.get("note", ""),
                contract_id,
            ),
        )
        conn.commit()


def delete_contract(contract_id: int):
    with get_db() as conn:
        room_id = conn.execute(
            "SELECT room_id FROM contract WHERE contract_id = ?", (contract_id,)
        ).fetchone()
        
        if room_id:
            status = conn.execute(
                "SELECT contract_status FROM contract WHERE contract_id = ?", (contract_id,)
            ).fetchone()[0]
            if status == "active":
                conn.execute(
                    "UPDATE room SET status = 0 WHERE room_id = ?", (room_id[0],)
                )
        
        conn.execute("UPDATE contract SET is_deleted = 1 WHERE contract_id = ?", (contract_id,))
        conn.commit()


def end_contract(contract_id: int):
    with get_db() as conn:
        room_id = conn.execute(
            "SELECT room_id FROM contract WHERE contract_id = ?", (contract_id,)
        ).fetchone()
        
        if room_id:
            conn.execute(
                "UPDATE room SET status = 0 WHERE room_id = ?", (room_id[0],)
            )
        
        conn.execute(
            """
            UPDATE contract 
            SET contract_status = 'ended', 
                end_ymd = date('now'),
                updated_at = CURRENT_TIMESTAMP
            WHERE contract_id = ?
            """,
            (contract_id,),
        )
        conn.commit()


def get_contract_by_id(contract_id: int):
    with get_db() as conn:
        return conn.execute(
            """
            SELECT c.*, r.room_name, t.full_name
            FROM contract c
            JOIN room r ON c.room_id = r.room_id
            JOIN tenant t ON c.tenant_id = t.tenant_id
            WHERE c.contract_id = ? AND c.is_deleted = 0
            """,
            (contract_id,),
        ).fetchone()


def get_available_rooms():
    with get_db() as conn:
        return conn.execute(
            """
            SELECT room_id, room_name, base_rent 
            FROM room 
            WHERE status = 0 AND is_deleted = 0 
            ORDER BY room_id
            """
        ).fetchall()


def get_tenants_without_active_contract():
    with get_db() as conn:
        return conn.execute(
            """
            SELECT t.tenant_id, t.full_name, t.phone
            FROM tenant t
            LEFT JOIN contract c ON t.tenant_id = c.tenant_id AND c.contract_status = 'active' AND c.is_deleted = 0
            WHERE t.is_deleted = 0
            GROUP BY t.tenant_id
            HAVING COUNT(CASE WHEN c.contract_id IS NOT NULL THEN 1 END) = 0
            """
        ).fetchall()


def export_contract_to_pdf(contract_id):
    """
    Export contract to PDF
    
    Args:
        contract_id (int): ID of the contract to export
        
    Returns:
        str: Path to the generated PDF file
    """
    contract = get_contract_by_id(contract_id)
    if not contract:
        raise ValueError("Contract not found")
    
    # Prepare contract data for PDF generation
    contract_data = dict(contract)
    
    # Create output directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Generate PDF filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"contract_{contract_id}_{timestamp}.pdf"
    output_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Generate the PDF
    create_contract_pdf(contract_data, output_path)
    
    return output_path