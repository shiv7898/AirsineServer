import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import SessionLocal
import app.models as models
from web.admin import to_numeric_or_string, safe_getattr
from datetime import datetime

db = SessionLocal()
try:
    pats_docs = db.query(models.User).all()
    dists = db.query(models.Distributor).all()
    staff = db.query(models.AdminStaff).all()
    supers = db.query(models.SuperAdmin).all()
    users = pats_docs + dists + staff + supers
    users.sort(key=lambda u: u.created_at or datetime.min, reverse=True)
    
    serialized = [{
        "id": u.id,
        "custom_id": u.custom_id,
        "name": u.name,
        "email": u.email,
        "role": u.role or (
            "distributor" if isinstance(u, models.Distributor) else
            "super_admin" if isinstance(u, models.SuperAdmin) else
            "admin" if isinstance(u, models.AdminStaff) else
            "patient"
        ),
        "phone": to_numeric_or_string(u.phone),
        "gender": u.gender,
        "age": to_numeric_or_string(u.age),
        "dob": u.dob,
        "homeAddress": u.home_address,
        "area": u.area,
        "district": u.district,
        "state": u.state,
        "pincode": to_numeric_or_string(u.pincode),
        "hospital": safe_getattr(u, "hospital"),
        "specialisation": safe_getattr(u, "specialisation"),
        "qualification": safe_getattr(u, "qualification"),
        "experience": safe_getattr(u, "experience"),
        "companyName": safe_getattr(u, "company_name"),
        "businessType": safe_getattr(u, "business_type"),
        "distributorType": safe_getattr(u, "distributor_type"),
        "licenseNumber": safe_getattr(u, "license_number"),
        "referralCode": safe_getattr(u, "referral_code"),
        "permissions": safe_getattr(u, "permissions"),
        "status": u.status or "Active",
        "verificationStatus": safe_getattr(u, "verification_status") or "Verified",
        "commission": safe_getattr(u, "commission") or 0.0,
        "discount": safe_getattr(u, "discount") or 0.0,
    } for u in users]
    
    print(json.dumps(serialized, indent=2))
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
