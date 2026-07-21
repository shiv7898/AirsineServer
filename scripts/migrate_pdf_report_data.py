"""
Migration: Add missing columns to pdf_report_data table.
Run once with:  python scripts/migrate_pdf_report_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text

COLUMNS = [
    ("app_user_name",  "VARCHAR"),
    ("app_user_email", "VARCHAR"),
    ("patient_details","TEXT"),
    ("total_days",     "INTEGER"),
    ("clinical_logs",  "TEXT"),
    ("pdf_base64",     "TEXT"),
]

def column_exists(conn, table, col):
    result = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": table, "c": col})
    return result.fetchone() is not None

with engine.connect() as conn:
    for col_name, col_type in COLUMNS:
        if column_exists(conn, "pdf_report_data", col_name):
            print(f"  SKIP  {col_name} (already exists)")
        else:
            conn.execute(text(
                f"ALTER TABLE pdf_report_data ADD COLUMN {col_name} {col_type}"
            ))
            print(f"  ADDED {col_name} {col_type}")
    conn.commit()

print("\nMigration complete.")
