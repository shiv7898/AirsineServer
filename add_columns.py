import psycopg2

try:
    conn = psycopg2.connect("postgresql://postgres:7410@localhost/hospitaldb")
    cur = conn.cursor()
    cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS customer_discount FLOAT DEFAULT 0.0;")
    cur.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS distributor_discount FLOAT DEFAULT 0.0;")
    conn.commit()
    print("Columns added successfully.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals() and conn:
        conn.close()
