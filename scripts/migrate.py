"""
scripts/migrate.py

Run all pending schema migrations.
Safe to run multiple times — each migration checks before applying.

Usage:
    python scripts/migrate.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.database import engine


MIGRATIONS = [
    {
        "table": "products",
        "column": "target_audience",
        "sql": "ALTER TABLE products ADD COLUMN target_audience VARCHAR DEFAULT 'patient_doctor';",
        "description": "Add target_audience to products",
    },
    {
        "table": "orders",
        "column": "user_role",
        "sql": "ALTER TABLE orders ADD COLUMN user_role VARCHAR DEFAULT 'patient';",
        "description": "Add user_role to orders",
    },
    {
        "table": "support_queries",
        "column": "user_role",
        "sql": "ALTER TABLE support_queries ADD COLUMN user_role VARCHAR DEFAULT 'patient';",
        "description": "Add user_role to support_queries",
    },
    {
        "table": "pdf_report_data",
        "column": "user_role",
        "sql": "ALTER TABLE pdf_report_data ADD COLUMN user_role VARCHAR DEFAULT 'patient';",
        "description": "Add user_role to pdf_report_data",
    },
    {
        "table": "distributors",
        "column": "referral_code",
        "sql": "ALTER TABLE distributors ADD COLUMN referral_code VARCHAR UNIQUE;",
        "description": "Add referral_code to distributors",
    },
    {
        "table": "support_queries",
        "column": "resolution_message",
        "sql": "ALTER TABLE support_queries ADD COLUMN resolution_message TEXT;",
        "description": "Add resolution_message to support_queries",
    },
    {
        "table": "support_queries",
        "column": "resolved_at",
        "sql": "ALTER TABLE support_queries ADD COLUMN resolved_at TIMESTAMP;",
        "description": "Add resolved_at to support_queries",
    },
]


def column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            f"WHERE table_name='{table}' AND column_name='{column}';"
        )
    )
    return result.fetchone() is not None


def run_migrations():
    print("Running database migrations...")
    with engine.begin() as conn:
        for migration in MIGRATIONS:
            if column_exists(conn, migration["table"], migration["column"]):
                print(f"  [SKIP] {migration['description']} (already exists)")
            else:
                conn.execute(text(migration["sql"]))
                print(f"  [OK]   {migration['description']}")
    print("Migrations complete.")


if __name__ == "__main__":
    run_migrations()
