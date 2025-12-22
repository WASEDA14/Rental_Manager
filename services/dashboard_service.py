from database.db import get_db
from datetime import datetime

def get_dashboard_stats():
    with get_db() as conn:
        # Get room statistics
        room_stats = conn.execute(
            """
            SELECT 
                COUNT(*) as total_rooms,
                SUM(CASE WHEN status = 'Đang thuê' THEN 1 ELSE 0 END) as occupied_rooms
            FROM room 
            WHERE is_deleted = 0
            """
        ).fetchone()
        
        # Get tenant statistics
        tenant_count = conn.execute(
            """
            SELECT COUNT(DISTINCT tenant_id) 
            FROM tenant
            WHERE is_deleted = 0
            """
        ).fetchone()[0]
        
        # Get current month's payments
        current_month = datetime.now().strftime('%Y-%m')
        monthly_payment = conn.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM bill
            WHERE strftime('%Y-%m', paid_ymd) = ?
            AND paid_status = 'paid'
            AND is_deleted = 0
            """,
            (current_month,)
        ).fetchone()[0]
    
    return {
        'total_rooms': room_stats['total_rooms'] or 0,
        'occupied_rooms': room_stats['occupied_rooms'] or 0,
        'available_rooms': (room_stats['total_rooms'] or 0) - (room_stats['occupied_rooms'] or 0),
        'total_tenants': tenant_count or 0,
        'monthly_payment': monthly_payment or 0.0
    }
