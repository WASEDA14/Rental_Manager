# services/auth_service.py
from typing import Optional, Dict, Any
from datetime import datetime
from database.db import get_db


class AuthService:

    def authenticate_user(
        self,
        login_id: str,
        login_password: str
    ) -> Optional[Dict[str, Any]]:

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT login_id, user_name, email
                FROM user
                WHERE login_id = ?
                  AND login_password = ?
            """, (login_id, login_password))

            row = cursor.fetchone()
            return dict(row) if row else None

    def log_login_attempt(self, login_id: str, success: bool) -> None:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO login_attempts
                (login_id, attempt_time, success)
                VALUES (?, ?, ?)
            """, (
                login_id,
                datetime.now().isoformat(),
                int(success)
            ))
