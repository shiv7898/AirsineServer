import sys
import os

# Add the parent directory to sys.path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import SessionLocal
import models

def migrate_users():
    db = SessionLocal()
    try:
        # Get all users from legacy users table
        legacy_users = db.query(models.User).all()
        
        migrated_patients = 0
        migrated_doctors = 0
        
        for user in legacy_users:
            if user.role == "patient":
                # Check if patient already exists
                existing = db.query(models.Patient).filter(models.Patient.email == user.email).first()
                if not existing:
                    new_patient = models.Patient(
                        custom_id=user.custom_id,
                        name=user.name,
                        email=user.email,
                        password=user.password,
                        role=user.role,
                        phone=user.phone,
                        gender=user.gender,
                        age=user.age,
                        dob=user.dob,
                        home_address=user.home_address,
                        area=user.area,
                        district=user.district,
                        state=user.state,
                        pincode=user.pincode,
                        referral_code=user.referral_code,
                        profile_image=user.profile_image,
                        status=user.status,
                        verification_status=user.verification_status,
                        created_at=user.created_at,
                        last_login=user.last_login
                    )
                    db.add(new_patient)
                    db.flush() # get ID
                    
                    # Update related tables to use the new patient ID and user_role
                    db.query(models.Order).filter(models.Order.user_id == user.id).update(
                        {"user_id": new_patient.id, "user_role": "patient"}
                    )
                    db.query(models.SupportQuery).filter(models.SupportQuery.user_id == user.id).update(
                        {"user_id": new_patient.id, "user_role": "patient"}
                    )
                    db.query(models.PdfReportData).filter(models.PdfReportData.user_id == user.id).update(
                        {"user_id": new_patient.id, "user_role": "patient"}
                    )
                    db.query(models.TherapyData).filter(models.TherapyData.patient_id == user.id).update(
                        {"patient_id": new_patient.id}
                    )
                    db.query(models.MachineSettings).filter(models.MachineSettings.patient_id == user.id).update(
                        {"patient_id": new_patient.id}
                    )
                    migrated_patients += 1

            elif user.role == "doctor":
                # Check if doctor already exists
                existing = db.query(models.Doctor).filter(models.Doctor.email == user.email).first()
                if not existing:
                    new_doctor = models.Doctor(
                        custom_id=user.custom_id,
                        name=user.name,
                        email=user.email,
                        password=user.password,
                        role=user.role,
                        phone=user.phone,
                        gender=user.gender,
                        age=user.age,
                        dob=user.dob,
                        home_address=user.home_address,
                        area=user.area,
                        district=user.district,
                        state=user.state,
                        pincode=user.pincode,
                        hospital=user.hospital,
                        specialisation=user.specialisation,
                        qualification=user.qualification,
                        experience=user.experience,
                        referral_code=user.referral_code,
                        profile_image=user.profile_image,
                        status=user.status,
                        verification_status=user.verification_status,
                        created_at=user.created_at,
                        last_login=user.last_login
                    )
                    db.add(new_doctor)
                    db.flush() # get ID

                    # Update related tables
                    db.query(models.MachineSettings).filter(models.MachineSettings.doctor_id == user.id).update(
                        {"doctor_id": new_doctor.id}
                    )
                    migrated_doctors += 1

        db.commit()
        print(f"Migration completed successfully. Migrated {migrated_patients} patients and {migrated_doctors} doctors.")
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting migration of users to Patient and Doctor tables...")
    migrate_users()
