import sys
import os

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from core.config import settings

def run_migration():
    DATABASE_URL = settings.DATABASE_URL
    print(f"Connecting to {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.begin() as conn:
            columns_to_add = {
                "product_code": "VARCHAR",
                "product_images": "TEXT",
                "brand": "VARCHAR",
                "model_name": "VARCHAR",
                "selling_price": "FLOAT",
                "referral_discount": "FLOAT DEFAULT 0.0",
                "tax_gst": "FLOAT DEFAULT 0.0",
                "stock_pieces": "INTEGER DEFAULT 0",
                "product_status": "VARCHAR DEFAULT 'Active'"
            }
            for col_name, col_type in columns_to_add.items():
                result = conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='products' AND column_name='{col_name}';"))
                if result.fetchone():
                    print(f"Column '{col_name}' already exists. Skipping.")
                else:
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type};"))
                    print(f"Successfully added '{col_name}' column to 'products' table.")
    except Exception as e:
        print(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
