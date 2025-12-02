import sqlite3
from pathlib import Path

# import UPDATE

DB_PATH = Path(__file__).resolve().parent / "rental_manager.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection() -> sqlite3.Connection:

    conn = sqlite3.connect(DB_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql = f.read()
        conn.executescript(sql)
        conn.commit()

    return conn


if __name__ == "__main__":
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", cur.fetchall())
    conn.close()
