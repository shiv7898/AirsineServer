import sys
import os
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
import app.models as models

db = SessionLocal()
try:
    dist = db.query(models.Distributor).filter(models.Distributor.id == 1).first()
    if dist:
        print(f"Before update: ID: {dist.id}, Name: {dist.name}, Verification Status: {dist.verification_status}")
        
        # Let's simulate the API update logic
        update_dict = {
            "verification_status": "Verified" if dist.verification_status != "Verified" else "Pending"
        }
        
        mapping = {
            "homeAddress": "home_address",
            "companyName": "company_name",
            "businessType": "business_type",
            "distributorType": "distributor_type",
            "licenseNumber": "license_number",
            "verificationStatus": "verification_status",
            "hospital": "hospital",
            "specialisation": "specialisation",
            "qualification": "qualification",
            "experience": "experience",
            "permissions": "permissions"
        }
        
        for key, value in update_dict.items():
            db_key = mapping.get(key, key)
            has_attr = hasattr(dist, db_key)
            print(f"Key: {key}, db_key: {db_key}, hasattr: {has_attr}")
            if has_attr:
                setattr(dist, db_key, value)
                
        db.commit()
        db.refresh(dist)
        print(f"After update: ID: {dist.id}, Name: {dist.name}, Verification Status: {dist.verification_status}")
    else:
        print("Distributor ID 1 not found!")
finally:
    db.close()
