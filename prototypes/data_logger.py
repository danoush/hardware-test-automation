import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent / "hvm_test_factory.db"


def initialize_production_database(db_path=DEFAULT_DB_PATH):
    """Creates a local relational database to log wafer-level test parameters."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS die_test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            wafer_id TEXT,
            die_number INTEGER,
            peak_power_dbm REAL,
            status TEXT
        )
    """)
    conn.commit()
    return conn
