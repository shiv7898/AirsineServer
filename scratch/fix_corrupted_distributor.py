import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
import app.models as models

db = SessionLocal()
try:
    print("Fixing corrupted distributor data...")
    
    # 1. Update Distributor ID 1 back to original values
    dist = db.query(models.Distributor).filter(models.Distributor.id == 1).first()
    if dist:
        dist.name = "Rish2"
        dist.email = "rishi2@gmail.com"
        db.commit()
        print("Distributor ID 1 restored: Name='Rish2', Email='rishi2@gmail.com'")
    else:
        print("Distributor ID 1 not found!")
        
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
