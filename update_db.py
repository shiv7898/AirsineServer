from sqlalchemy import text
from database import engine

def add_permissions_column():
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN permissions TEXT;"))
            print("Successfully added 'permissions' column to 'users' table.")
    except Exception as e:
        print(f"Error adding column: {e}")
        if "already exists" in str(e).lower():
            print("Column already exists. Skipping.")

if __name__ == "__main__":
    add_permissions_column()
