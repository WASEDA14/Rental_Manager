from database.db import get_db
from datetime import datetime

def get_dashboard_stats():
    try:
        with get_db() as conn:
            # Set row factory to return dictionaries
            conn.row_factory = lambda cursor, row: {}

            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_rooms,
                    SUM(CASE WHEN status = 'Đang thuê' THEN 1 ELSE 0 END) as occupied_rooms
                FROM room 
                WHERE is_deleted = 0
                """
            )
            room_stats = cursor.fetchone() or {}

            cursor.execute(
                """
                SELECT COUNT(DISTINCT tenant_id) as count
                FROM tenant
                WHERE is_deleted = 0
                """
            )
            tenant_count = (cursor.fetchone() or {}).get('count', 0)

            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute(
                """
                SELECT 
                    SUM(CASE WHEN paid_status = 'paid' THEN 1 ELSE 0) as paid_bills,
                    COUNT(*) as total_bills
                FROM bill
                WHERE bill_month = ?
                AND is_deleted = 0
                """,
                (current_month,)
            )
            bill_stats = cursor.fetchone() or {}

            total_rooms = int(room_stats.get('total_rooms', 0) or 0)
            occupied_rooms = int(room_stats.get('occupied_rooms', 0) or 0)
            paid_bills = int(bill_stats.get('paid_bills', 0) or 0)
            total_bills = int(bill_stats.get('total_bills', 0) or 0)
            return {
                'total_rooms': total_rooms,
                'occupied_rooms': occupied_rooms,
                'available_rooms': total_rooms - occupied_rooms,
                'total_tenants': tenant_count,
                'paid_bills': paid_bills,
                'total_bills': total_bills
            }
    except Exception as e:
        print(f"[ERROR] in get_dashboard_stats: {str(e)}")
        return {
            'total_rooms': 0,
            'occupied_rooms': 0,
            'available_rooms': 0,
            'total_tenants': 0,
            'paid_bills': 0,
            'total_bills': 0
        }
