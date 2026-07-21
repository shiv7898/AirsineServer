import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
import app.models as models

db = SessionLocal()
try:
    print("=== Database State ===")
    
    for u in db.query(models.User).all():
        print(f"User: ID={u.id}, Name={u.name}, Role={u.role}, Email={u.email}, VerStatus={getattr(u, 'verification_status', 'N/A')}")
        
    for d in db.query(models.Distributor).all():
        print(f"Distributor: ID={d.id}, Name={d.name}, Role={d.role}, Email={d.email}, VerStatus={getattr(d, 'verification_status', 'N/A')}")
        
    for s in db.query(models.AdminStaff).all():
        print(f"AdminStaff: ID={s.id}, Name={s.name}, Role={s.role}, Email={s.email}, Status={s.status}")
        
    for sp in db.query(models.SuperAdmin).all():
        print(f"SuperAdmin: ID={sp.id}, Name={sp.name}, Role={sp.role}, Email={sp.email}")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
