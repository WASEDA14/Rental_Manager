# services/report.py
from database.db import get_db
from datetime import datetime, timedelta


def get_room_report():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM room WHERE is_deleted = 0").fetchone()[0]
        occupied = conn.execute(
            "SELECT COUNT(*) FROM room WHERE status = 1 AND is_deleted = 0"
        ).fetchone()[0]
        available = conn.execute(
            "SELECT COUNT(*) FROM room WHERE status = 0 AND is_deleted = 0"
        ).fetchone()[0]
        maintenance = total - occupied - available
        return {
            "total": total,
            "occupied": occupied,
            "available": available,
            "maintenance": maintenance,
        }


def get_tenant_report():
    with get_db() as conn:
        active = conn.execute(
            """
            SELECT COUNT(DISTINCT t.tenant_id) 
            FROM tenant t
            JOIN contract c ON t.tenant_id = c.tenant_id
            WHERE c.contract_status = 'active' AND c.is_deleted = 0 AND t.is_deleted = 0
        """
        ).fetchone()[0]

        this_month = datetime.now().strftime("%Y-%m")
        new_this_month = conn.execute(
            """
            SELECT COUNT(DISTINCT t.tenant_id)
            FROM tenant t
            JOIN contract c ON t.tenant_id = c.tenant_id
            WHERE strftime('%Y-%m', c.start_ymd) = ? AND c.contract_status = 'active' AND c.is_deleted = 0
        """,
            (this_month,),
        ).fetchone()[0]

        return {"active": active, "new_this_month": new_this_month}


def get_contract_report():
    with get_db() as conn:
        today = datetime.now().date()
        soon = today + timedelta(days=30)
        this_month = datetime.now().strftime("%Y-%m")

        new_this_month = conn.execute(
            """
            SELECT COUNT(*) FROM contract 
            WHERE strftime('%Y-%m', start_ymd) = ? AND contract_status = 'active' AND is_deleted = 0
        """,
            (this_month,),
        ).fetchone()[0]

        soon_expire = conn.execute(
            """
            SELECT COUNT(*) FROM contract 
            WHERE end_ymd BETWEEN date('now') AND date('now', '+30 days')
              AND contract_status = 'active' AND is_deleted = 0
        """
        ).fetchone()[0]

        ended = conn.execute(
            "SELECT COUNT(*) FROM contract WHERE contract_status = 'ended' AND is_deleted = 0"
        ).fetchone()[0]

        return {
            "new_this_month": new_this_month,
            "soon_expire": soon_expire,
            "ended": ended,
        }


def get_bill_report():
    with get_db() as conn:
        unpaid = conn.execute(
            "SELECT COUNT(*) FROM bill WHERE paid_status = 'unpaid' AND is_deleted = 0"
        ).fetchone()[0]
        paid = conn.execute(
            "SELECT COUNT(*) FROM bill WHERE paid_status = 'paid' AND is_deleted = 0"
        ).fetchone()[0]
        return {"unpaid": unpaid, "paid": paid, "total": unpaid + paid}


def get_revenue_last_6_months():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT bill_month, COALESCE(SUM(total_amount), 0) as revenue
            FROM bill 
            WHERE paid_status = 'paid' AND is_deleted = 0
            GROUP BY bill_month
            ORDER BY bill_month DESC
            LIMIT 6
        """
        ).fetchall()

        result = []
        for row in reversed(rows):
            result.append({"month": row["bill_month"], "revenue": int(row["revenue"])})

        while len(result) < 6:
            result.insert(0, {"month": "—", "revenue": 0})

        return result
    return result