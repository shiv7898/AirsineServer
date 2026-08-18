"""
services/user_service.py

Centralized user business logic.
Handles creating, fetching, updating, and deleting users
across all roles: patient, doctor, distributor, admin, sub_admin, super_admin.
"""
import random
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

import models
from core.security import hash_password
from helpers.validators import (
    validate_email,
    validate_password,
    validate_phone,
    validate_pincode,
    validate_age,
)


class UserService:

    # ------------------------------------------------------------------
    # CUSTOM ID GENERATION
    # ------------------------------------------------------------------

    @staticmethod
    def generate_custom_id(db: Session, role: str) -> str:
        """Generate a sequential AIR-XXX formatted custom_id for a given role."""
        prefix_map = {
            "patient":     "AIR-P",
            "doctor":      "AIR-DR",
            "distributor": "AIR-DI",
            "admin":       "AIR-A",
            "super_admin": "AIR-SA",
            "sub_admin":   "AIR-SBA",
        }
        prefix = prefix_map.get(role, "AIR-U")

        model_map = {
            "distributor": models.Distributor,
            "super_admin": models.SuperAdmin,
            "admin": models.AdminStaff,
            "sub_admin": models.AdminStaff,
            "doctor": models.Doctor,
        }
        model = model_map.get(role, models.Patient)

        existing = db.query(model).filter(
            model.role == role,
            model.custom_id.isnot(None),
        ).all()

        max_num = 0
        for u in existing:
            if u.custom_id and u.custom_id.startswith(prefix):
                try:
                    num = int(u.custom_id[len(prefix):])
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    pass

        return f"{prefix}{max_num + 1:03d}"

    @staticmethod
    def generate_unique_referral_code(db: Session) -> str:
        """Generate a unique 8-character alphanumeric referral code."""
        import string
        import random
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # Check if this code exists in Patient, Doctor, or Distributor
            found = False
            for model in [models.Patient, models.Doctor, models.Distributor]:
                if db.query(model).filter(model.referral_code == code).first():
                    found = True
                    break
            if not found:
                return code

    # ------------------------------------------------------------------
    # EMAIL UNIQUENESS CHECKS
    # ------------------------------------------------------------------

    @staticmethod
    def is_email_taken(db: Session, email: str) -> bool:
        """Check if email is already registered across ALL user tables."""
        email_lower = email.lower().strip()
        models_to_check = [
            models.Patient, models.Doctor, models.Distributor,
            models.AdminStaff, models.SuperAdmin,
        ]
        for model in models_to_check:
            if db.query(model).filter(model.email == email_lower).first():
                return True
        return False

    @staticmethod
    def is_email_taken_by_other(
        db: Session, email: str, exclude_user_id: int, exclude_role: str
    ) -> bool:
        """Check if email belongs to a DIFFERENT user (for update validation)."""
        email_lower = email.lower().strip()

        checks = [
            (models.Patient, "patient"),
            (models.Doctor, "doctor"),
            (models.Distributor, "distributor"),
            (models.AdminStaff, "admin"),
            (models.SuperAdmin, "super_admin"),
        ]
        for model, role_name in checks:
            user = db.query(model).filter(model.email == email_lower).first()
            if user:
                is_excluded = (exclude_role == role_name and user.id == exclude_user_id)
                if not is_excluded:
                    return True
        return False

    @staticmethod
    def find_user_by_email(db: Session, email: str):
        """Find a user across all tables by email address."""
        email_lower = email.lower().strip()
        for model in [
            models.Patient, models.Doctor, models.Distributor,
            models.AdminStaff, models.SuperAdmin,
        ]:
            user = db.query(model).filter(model.email == email_lower).first()
            if user:
                return user
        return None

    @staticmethod
    def find_user_by_phone(db: Session, phone: str):
        """Find a user across all tables by phone number (strips +91 prefix)."""
        phone_clean = str(phone).strip()
        if phone_clean.startswith("+91"):
            phone_clean = phone_clean[3:]
        if phone_clean.startswith("91") and len(phone_clean) == 12:
            phone_clean = phone_clean[2:]

        for model in [models.Patient, models.Doctor, models.Distributor]:
            user = db.query(model).filter(model.phone == phone_clean).first()
            if user:
                return user
        return None

    # ------------------------------------------------------------------
    # FETCH USERS
    # ------------------------------------------------------------------

    @staticmethod
    def get_all_users(db: Session) -> List[dict]:
        """
        Fetch all users from all tables and return a unified list.
        Each entry includes a 'role' key.
        """
        results = []

        patients = db.query(models.Patient).all()
        for p in patients:
            results.append({
                "id": p.id,
                "custom_id": p.custom_id,
                "name": p.name,
                "email": p.email,
                "phone": p.phone,
                "role": "patient",
                "gender": p.gender,
                "age": p.age,
                "referral_code": p.referral_code,
                "is_active": getattr(p, "is_active", True),
            })

        doctors = db.query(models.Doctor).all()
        for d in doctors:
            results.append({
                "id": d.id,
                "custom_id": d.custom_id,
                "name": d.name,
                "email": d.email,
                "phone": d.phone,
                "role": "doctor",
                "gender": d.gender,
                "age": d.age,
                "referral_code": d.referral_code,
                "is_active": getattr(d, "is_active", True),
            })

        distributors = db.query(models.Distributor).all()
        for dist in distributors:
            results.append({
                "id": dist.id,
                "custom_id": dist.custom_id,
                "name": dist.name,
                "email": dist.email,
                "phone": dist.phone,
                "role": "distributor",
                "gender": dist.gender,
                "age": dist.age,
                "companyName": dist.company_name,
                "commission": getattr(dist, "commission", 0),
                "referral_code": dist.referral_code,
                "is_active": getattr(dist, "is_active", True),
            })

        staff = db.query(models.AdminStaff).all()
        for s in staff:
            results.append({
                "id": s.id,
                "custom_id": s.custom_id,
                "name": s.name,
                "email": s.email,
                "phone": s.phone,
                "role": s.role,
                "gender": s.gender,
                "age": s.age,
                "permissions": s.permissions,
                "is_active": getattr(s, "is_active", True),
            })

        return results

    @staticmethod
    def get_user_by_id(db: Session, user_id: int, role: str):
        """Fetch a single user by ID and role, returns the model instance."""
        model_map = {
            "patient": models.Patient,
            "doctor": models.Doctor,
            "distributor": models.Distributor,
            "admin": models.AdminStaff,
            "sub_admin": models.AdminStaff,
            "super_admin": models.SuperAdmin,
        }
        model = model_map.get(role)
        if not model:
            raise HTTPException(status_code=400, detail=f"Unknown role: {role}")
        user = db.query(model).filter(model.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # ------------------------------------------------------------------
    # CREATE USER
    # ------------------------------------------------------------------

    @staticmethod
    def create_user(db: Session, payload: dict) -> Tuple[object, str]:
        """
        Create a new user of any role.
        payload keys: name, email, password, phone, role, gender, age, dob,
                      homeAddress, area, district, state, pincode,
                      + role-specific fields.
        Returns (new_user_object, role_string)
        """
        role = payload.get("role", "patient")

        validated_email = validate_email(payload["email"])
        if UserService.is_email_taken(db, validated_email):
            raise HTTPException(status_code=409, detail="Email already registered")

        validated_password = validate_password(payload["password"])
        validated_phone = validate_phone(payload["phone"])
        validated_age = validate_age(payload.get("age", 0))
        validated_pincode = validate_pincode(payload.get("pincode", "000000"))

        common_fields = dict(
            name=payload["name"].strip(),
            email=validated_email,
            password=hash_password(validated_password),
            phone=validated_phone,
            gender=payload.get("gender", ""),
            age=validated_age,
            dob=payload.get("dob", "01-01-2000"),
            home_address=payload.get("homeAddress", "N/A"),
            area=payload.get("area", "N/A"),
            district=payload.get("district", "N/A"),
            state=payload.get("state", "N/A"),
            pincode=validated_pincode,
        )

        try:
            if role == "patient":
                new_user = models.Patient(**common_fields)
                new_user.referral_code = UserService.generate_unique_referral_code(db)
            elif role == "doctor":
                new_user = models.Doctor(
                    **common_fields,
                    hospital=payload.get("hospital"),
                    specialisation=payload.get("specialisation"),
                    qualification=payload.get("qualification"),
                    experience=payload.get("experience"),
                )
                new_user.referral_code = UserService.generate_unique_referral_code(db)
            elif role == "distributor":
                new_user = models.Distributor(
                    **common_fields,
                    company_name=payload.get("companyName"),
                    business_type=payload.get("businessType"),
                    license_number=payload.get("licenseNumber"),
                )
                new_user.referral_code = UserService.generate_unique_referral_code(db)
            elif role in ("admin", "sub_admin"):
                new_user = models.AdminStaff(
                    **common_fields,
                    role=role,
                    permissions=payload.get("permissions", "{}"),
                )
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported role: {role}")

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user, role

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    # ------------------------------------------------------------------
    # DELETE USER
    # ------------------------------------------------------------------

    @staticmethod
    def delete_user(db: Session, user_id: int, role: str) -> dict:
        """Delete a user by ID and role."""
        user = UserService.get_user_by_id(db, user_id, role)
        try:
            db.delete(user)
            db.commit()
            return {"message": f"User deleted successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
