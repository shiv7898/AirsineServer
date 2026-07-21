import sqlite3
import json

conn = sqlite3.connect('hospital.db')
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT * FROM users WHERE id IN (6, 17)").fetchall()
with open('db_dump.txt', 'w') as f:
    for row in rows:
        f.write(json.dumps(dict(row)) + "\n")
