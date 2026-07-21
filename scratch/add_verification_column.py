import sys
import os
from sqlalchemy import text

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal

db = SessionLocal()
try:
    print("Running migration to add verification_status columns...")
    
    # 1. Add verification_status to admin_staff if not exists
    db.execute(text("ALTER TABLE admin_staff ADD COLUMN IF NOT EXISTS verification_status VARCHAR DEFAULT 'Verified';"))
    # 2. Add verification_status to super_admins if not exists
    db.execute(text("ALTER TABLE super_admins ADD COLUMN IF NOT EXISTS verification_status VARCHAR DEFAULT 'Verified';"))
    
    db.commit()
    print("Migration successful! Verification status columns added successfully.")
except Exception as e:
    db.rollback()
    print(f"Migration error: {e}")
finally:
    db.close()
