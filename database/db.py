# db.py
import sqlite3
from pathlib import Path

# Đường dẫn database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "rental_manager.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_db() -> sqlite3.Connection:
    """
    Mỗi lần gọi -> mở 1 connection mới
    Dùng xong -> đóng ngay (qua context manager)
    Cách này là CHUẨN với SQLite desktop app
    """
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    is_new_db = not DB_PATH.exists()

    conn = sqlite3.connect(
        DB_PATH,
        timeout=10  # tránh treo vô hạn
    )
    conn.row_factory = sqlite3.Row

    # Pragmas an toàn
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

    # Tạo schema nếu DB mới
    if is_new_db:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()

    return conn


def list_tables():
    """In ra danh sách bảng + số dòng (debug)"""
    with get_db() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = cursor.fetchall()

        print("\n=== Database Tables ===")
        if not tables:
            print("No tables found.")
            return

        for i, row in enumerate(tables, 1):
            table_name = row["name"]
            print(f"\n{i}. Table: {table_name}")
            print("-" * 40)

            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                print(
                    f"  - {col['name']} {col['type']} "
                    f"{'NOT NULL' if col['notnull'] else ''} "
                    f"{'PK' if col['pk'] else ''}"
                )

            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table_name}")
            count = cursor.fetchone()["cnt"]
            print(f"  Rows: {count}")


if __name__ == "__main__":
    list_tables()
