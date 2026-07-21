import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
import app.models as models

db = SessionLocal()
try:
    print("=== Database Table Counts ===")
    
    users = db.query(models.User).all()
    print(f"User (Patient/Doctor) table count: {len(users)}")
    for u in users:
        print(f" - ID: {u.id}, Name: {u.name}, Role: {u.role}, Email: {u.email}")
        
    distributors = db.query(models.Distributor).all()
    print(f"Distributor table count: {len(distributors)}")
    for d in distributors:
        print(f" - ID: {d.id}, Name: {d.name}, Role: {d.role}, Email: {d.email}")
        
    staff = db.query(models.AdminStaff).all()
    print(f"AdminStaff table count: {len(staff)}")
    for s in staff:
        print(f" - ID: {s.id}, Name: {s.name}, Role: {s.role}, Email: {s.email}")
        
    supers = db.query(models.SuperAdmin).all()
    print(f"SuperAdmin table count: {len(supers)}")
    for sp in supers:
        print(f" - ID: {sp.id}, Name: {sp.name}, Role: {sp.role}, Email: {sp.email}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
