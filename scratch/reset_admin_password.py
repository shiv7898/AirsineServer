import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
import app.models as models
from app.core.auth import hash_password

db = SessionLocal()
try:
    admin = db.query(models.SuperAdmin).filter(models.SuperAdmin.email == "superadmin@airsine.com").first()
    if admin:
        admin.password = hash_password("Admin123")
        db.commit()
        print("Password updated successfully for superadmin@airsine.com to 'Admin123'")
    else:
        print("Super admin not found!")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
