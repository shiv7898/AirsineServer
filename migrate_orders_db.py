import sys
import os
from sqlalchemy import create_engine, text

# Add current dir to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

alter_statements = [
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS mrp_amount FLOAT DEFAULT 0.0;",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS product_discount_amount FLOAT DEFAULT 0.0;",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS referral_discount_amount FLOAT DEFAULT 0.0;",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS gst_amount FLOAT DEFAULT 0.0;",
    "ALTER TABLE orders ADD COLUMN IF NOT EXISTS order_number VARCHAR(255);",
    "UPDATE orders SET order_number = '#ORD-' || LPAD(id::text, 4, '0') WHERE order_number IS NULL;"
]

print("Starting migration...")
try:
    with engine.begin() as conn:
        for stmt in alter_statements:
            print(f"Executing: {stmt}")
            conn.execute(text(stmt))
    print("Migration successful!")
except Exception as e:
    print(f"Migration failed: {e}")
