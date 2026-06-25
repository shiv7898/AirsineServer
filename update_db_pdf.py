import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:7410@localhost/hospitaldb")

def update_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='pdf_report_data' and column_name='pdf_base64';
        """)
        
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE pdf_report_data ADD COLUMN pdf_base64 TEXT;")
            print("Successfully added pdf_base64 column to pdf_report_data table.")
        else:
            print("pdf_base64 column already exists in pdf_report_data table.")
            
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_db()
