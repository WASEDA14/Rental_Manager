# services/auth_service.py
import sqlite3
from typing import Optional, Dict
from datetime import datetime


class AuthService:
    def __init__(self, db_path: str = 'database/rental_manager.db'):
        self.db_path = db_path

    def authenticate_user(self, login_id: str, login_password: str) -> Optional[Dict]:
        """Authenticate a user with login_id and password"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT login_id, user_name, email 
                    FROM user 
                    WHERE login_id = ? AND login_password = ?
                """, (login_id, login_password))

                user = cursor.fetchone()
                return dict(user) if user else None

        except sqlite3.Error as e:
            print(f"Authentication error: {e}")
            return None

    def log_login_attempt(self, login_id: str, success: bool) -> bool:
        """Log a login attempt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS login_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        login_id TEXT NOT NULL,
                        attempt_time TEXT NOT NULL,
                        success INTEGER NOT NULL
                    )
                """)
                cursor.execute("""
                    INSERT INTO login_attempts 
                    (login_id, attempt_time, success)
                    VALUES (?, ?, ?)
                """, (login_id, datetime.now().isoformat(), int(success)))
                return True
        except sqlite3.Error as e:
            print(f"Error logging login attempt: {e}")
            return False