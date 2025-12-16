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
                contract_id, tenant_name, room_no, bill_month,
                elec_prev, elec_current, water_prev, water_current,
                electric_unit_price, water_unit_price,
                room_rent_amount, other_fee, total_amount, note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["contract_id"],
                tenant_name,
                room_name,
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


def export_bill_to_pdf(bill_id: int, output_dir: str = None) -> str:
    """
    Export a bill to PDF
    
    Args:
        bill_id: ID of the bill to export
        output_dir: Directory to save the PDF. If None, uses system temp directory
        
    Returns:
        Path to the generated PDF file
    """
    # Get bill data
    bill_data = get_bill_for_export(bill_id)
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), 'rental_manager', 'bills')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    filename = f"HoaDon_{bill_data['bill_code']}_{bill_data['bill_month'].replace('/', '-')}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Create the PDF
    create_bill_pdf(bill_data, output_path)
    
    return output_path


def get_contract_for_export(contract_id: int) -> dict:
    """Get contract data for PDF export"""
    with get_db() as conn:
        contract = conn.execute(
            """
            SELECT c.*, r.room_name, r.address as property_address,
                   t.full_name as tenant_name, t.phone, t.id_number,
                   t.permanent_address
            FROM contract c
            JOIN room r ON c.room_id = r.room_id
            JOIN tenant t ON c.tenant_id = t.tenant_id
            WHERE c.contract_id = ? AND c.is_deleted = 0
            """,
            (contract_id,)
        ).fetchone()
        
        if not contract:
            raise ValueError("Contract not found or has been deleted")
            
        # Convert to dict for easier access
        contract_dict = dict(contract)
        
        # Add additional fields if needed
        contract_dict['contract_code'] = f"HD{contract_id:06d}"
        contract_dict['company_address'] = "Số 1, Đường ABC, Quận 1, TP.HCM"
        contract_dict['payment_due_day'] = "05"  # Default payment due day
        
        # Format dates
        if 'start_date' in contract_dict and contract_dict['start_date']:
            if isinstance(contract_dict['start_date'], str):
                # If it's already a string, try to parse and reformat
                try:
                    dt = datetime.strptime(contract_dict['start_date'], '%Y-%m-%d')
                    contract_dict['start_date'] = dt.strftime('%d/%m/%Y')
                except:
                    pass
            else:
                # If it's a date object
                contract_dict['start_date'] = contract_dict['start_date'].strftime('%d/%m/%Y')
                
        if 'end_date' in contract_dict and contract_dict['end_date']:
            if isinstance(contract_dict['end_date'], str):
                try:
                    dt = datetime.strptime(contract_dict['end_date'], '%Y-%m-%d')
                    contract_dict['end_date'] = dt.strftime('%d/%m/%Y')
                except:
                    pass
            else:
                contract_dict['end_date'] = contract_dict['end_date'].strftime('%d/%m/%Y')
        
        return contract_dict


def export_contract_to_pdf(contract_id: int, output_dir: str = None) -> str:
    """
    Export a contract to PDF
    
    Args:
        contract_id: ID of the contract to export
        output_dir: Directory to save the PDF. If None, uses system temp directory
        
    Returns:
        Path to the generated PDF file
    """
    # Get contract data
    contract_data = get_contract_for_export(contract_id)
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = os.path.join(tempfile.gettempdir(), 'rental_manager', 'contracts')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename
    filename = f"HopDong_{contract_data['contract_code']}_{contract_data['tenant_name']}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Create the PDF
    create_contract_pdf(contract_data, output_path)
    
    return output_path