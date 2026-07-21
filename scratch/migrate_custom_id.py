import os
import sys
# Add current directory to sys.path so we can import from database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database import engine

def generate_custom_id(role, current_counts):
    prefix = ""
    if role == "patient":
        prefix = "AIR-P"
    elif role == "doctor":
        prefix = "AIR-DR"
    elif role == "distributor":
        prefix = "AIR-DI"
    elif role == "admin":
        prefix = "AIR-A"
    elif role == "super_admin":
        prefix = "AIR-SA"
    elif role == "sub_admin":
        prefix = "AIR-SBA"
    else:
        prefix = "AIR-U"
    
    current_counts[prefix] = current_counts.get(prefix, 0) + 1
    return f"{prefix}{current_counts[prefix]:03d}"

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN custom_id VARCHAR UNIQUE;"))
            conn.commit()
            print("Column custom_id added successfully.")
        except Exception as e:
            print(f"Column might already exist: {e}")
            conn.rollback()

        result = conn.execute(text("SELECT id, role FROM users ORDER BY id ASC"))
        users = result.fetchall()
        
        current_counts = {}
        
        for user_id, role in users:
            custom_id = generate_custom_id(role, current_counts)
            conn.execute(text("UPDATE users SET custom_id = :custom_id WHERE id = :id"), {"custom_id": custom_id, "id": user_id})
            
        conn.commit()
        print("Backfill completed.")

if __name__ == "__main__":
    migrate()
