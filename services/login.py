from database.db import get_db

def authenticate_user(username: str, password: str):
    conn = get_db()
    return conn.execute(
        "SELECT username FROM user WHERE username = ? AND password = ? AND is_deleted = 0",
        (username, password),
    ).fetchone()