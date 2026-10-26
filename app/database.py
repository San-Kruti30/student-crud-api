import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "students.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # lets us read rows like dictionaries
    return conn

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                date_of_birth   TEXT NOT NULL,
                email           TEXT UNIQUE,
                phone           TEXT,
                course          TEXT,
                address         TEXT,
                enrollment_date TEXT
            )
        """)