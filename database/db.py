import sqlite3
from pathlib import Path

# import UPDATE

DB_PATH = Path(__file__).resolve().parent / "rental_manager.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_db() -> sqlite3.Connection:
    # Make sure DB_PATH is a Path object
    db_path = Path(DB_PATH)
    
    # Create parent directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(str(db_path))
    
    # Only create schema if the database file is new
    if not db_path.exists() or db_path.stat().st_size == 0:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql = f.read()
            conn.executescript(sql)
            conn.commit()
    
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Use row factory for named access to columns
    conn.row_factory = sqlite3.Row
    
    return conn


if __name__ == "__main__":
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", cur.fetchall())
    conn.close()


def init_db():
    return None