import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("No DATABASE_URL found.")
    exit(1)

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE support_queries ADD COLUMN resolution_message TEXT;"))
        conn.commit()
        print("Column resolution_message added successfully.")
    except Exception as e:
        print(f"Error: {e}")
