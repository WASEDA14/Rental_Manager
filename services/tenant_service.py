from database.db import get_db
import re
from datetime import datetime

def get_all_tenant():
        conn = get_db()
        return conn.execute(
            """
        SELECT tenant_id, full_name, sex, phone, id_number,
               address, birth, note
        FROM tenant
        WHERE is_deleted = 0
        ORDER BY tenant_id DESC
    """
    ).fetchall()

def get_tennant_by_id(tennant_id: int):
        conn = get_db()
        return conn.execute("SELECT * FROM tennant WHERE tennant_id = ?", (tennant_id,)).fetchone()

PHONE_RE = re.compile(r'^\+?\d{7,15}$')

def validate_tenant(data: dict):
            # Required
            if not data.get("full_name") or not str(data["full_name"]).strip():
                raise ValueError("full_name là bắt buộc.")
            # sex: cho phép None hoặc 0/1/2
            sex = data.get("sex")
            if sex is not None:
                try:
                    sex = int(sex)
                except (TypeError, ValueError):
                    raise ValueError("sex phải là số (0,1,2) hoặc None.")
                if sex not in (0, 1, 2):
                    raise ValueError("sex phải có giá trị 0, 1 hoặc 2.")
            # phone: nếu có thì kiểm tra định dạng
            phone = data.get("phone")
            if phone:
                phone = str(phone).strip()
                if not PHONE_RE.match(phone):
                    raise ValueError("phone không hợp lệ. Chỉ cho phép chữ số (7-15 ký tự), có thể có dấu +.")
            # id_number: bắt buộc, lưu dưới dạng TEXT nhưng kiểm tra độ dài / ký tự
            id_number = data.get("id_number")
            if not id_number:
                raise ValueError("id_number là bắt buộc.")
            id_number = str(id_number).strip()
            if len(id_number) < 4 or len(id_number) > 30:
                raise ValueError("id_number có độ dài không hợp lệ (4-30 ký tự).")
            # birth: nếu có thì phải là YYYY-MM-DD
            birth = data.get("birth")
            if birth:
                if isinstance(birth, str):
                    try:
                        datetime.strptime(birth, "%Y-%m-%d")
                    except ValueError:
                        raise ValueError("birth phải ở định dạng 'YYYY-MM-DD'.")
                else:
                    raise ValueError("birth phải là chuỗi theo định dạng 'YYYY-MM-DD'.")
            # gộp và trả về phiên bản đã chuẩn hóa
            return {
                "full_name": str(data["full_name"]).strip(),
                "sex": sex,
                "phone": phone,
                "id_number": id_number,
                "address": (data.get("address") or "").strip(),
                "birth": birth,
                "note": (data.get("note") or "").strip(),
            }


        # ---------- Commands ----------
def create_tenant(data: dict):
    conn = get_db()
    conn.execute(
        """
        INSERT INTO tenant (full_name, sex, phone, id_number, address, birth, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data["full_name"],
            data["sex"],
            data["phone"],
            data["id_number"],
            data["address"],
            data["birth"],
            data["note"],
        ),
    )
    conn.commit()

def update_tenant(tenant_id: int, data: dict):
        conn = get_db()
        conn.execute(
            """
            UPDATE tenant SET full_name=?, sex=?, phone=?, id_number=?,
                              address=?, birth=?, note=?
            WHERE tenant_id = ?
        """,
            (
                data["full_name"],
                data["sex"],
                data["phone"],
                data["id_number"],
                data["address"],
                data["birth"],
                data["note"],
                tenant_id,
            ),
        )
        conn.commit()


def delete_tenant(tenant_id: int):
    conn = get_db()
    active = conn.execute(
        """
        SELECT 1 FROM contract WHERE tenant_id = ? AND contract_status = 'active' AND is_deleted = 0
    """,
        (tenant_id,),
    ).fetchone()
    if active:
        raise ValueError("Không thể xóa khách đang có hợp đồng hiệu lực!")
    conn.execute("UPDATE tenant SET is_deleted = 1 WHERE tenant_id = ?", (tenant_id,))
    conn.commit()
