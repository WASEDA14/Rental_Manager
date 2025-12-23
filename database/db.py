# database/db.py
import sqlite3
from pathlib import Path
import os
import sys

# Đường dẫn đúng dù chạy từ source hay từ .exe
if getattr(sys, "frozen", False):
    # Đang chạy từ file .exe → lấy thư mục tạm
    BASE_PATH = Path(sys._MEIPASS)
else:
    # Đang chạy từ source → lấy thư mục hiện tại
    BASE_PATH = Path(__file__).parent.parent

DB_PATH = BASE_PATH / "rental_manager.db"
SCHEMA_PATH = BASE_PATH / "database" / "schema.sql"


# Kết nối DB
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Khởi tạo DB từ schema.sql
def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy schema.sql tại: {SCHEMA_PATH}")

    with open(SCHEMA_PATH, encoding="utf-8") as f:
        get_db().executescript(f.read())
    get_db().commit()


# Tự động tạo DB nếu chưa có
if not DB_PATH.exists():
    init_db()