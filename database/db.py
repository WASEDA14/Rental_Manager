# database/db.py
import sqlite3
from pathlib import Path
import os
import sys

# =========================
# 1. PATH CHO RESOURCE (READ-ONLY)
# =========================
if getattr(sys, "frozen", False):
    # Khi chạy .exe (PyInstaller)
    RESOURCE_PATH = Path(sys._MEIPASS)
else:
    # Khi chạy source
    RESOURCE_PATH = Path(__file__).parent.parent

SCHEMA_PATH = RESOURCE_PATH / "database" / "schema.sql"

# =========================
# 2. PATH CHO DATA (READ-WRITE)
# =========================
APP_NAME = "RentalManager"

DATA_DIR = Path(os.getenv("APPDATA")) / APP_NAME
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "rental_manager.db"

# =========================
# 3. KẾT NỐI DB
# =========================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# 4. INIT DB TỪ SCHEMA
# =========================
def init_db():
    if DB_PATH.exists():
        return

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy schema.sql tại: {SCHEMA_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

# =========================
# 5. ASYNC INIT
# =========================
_db_initialized = False

def is_db_initialized():
    return _db_initialized

def initialize_db_async(callback=None):
    """Initialize database in a background thread"""
    import threading
    
    def init_in_thread():
        global _db_initialized
        try:
            init_db()
            _db_initialized = True
        except Exception as e:
            print(f"Error initializing database: {e}")
            _db_initialized = False
        finally:
            if callback:
                callback(_db_initialized)
    
    thread = threading.Thread(target=init_in_thread, daemon=True)
    thread.start()

# Initialize database in background on import
initialize_db_async()