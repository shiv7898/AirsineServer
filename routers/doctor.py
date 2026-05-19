from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime, timedelta
import models
import os
from schemas import MachineSettingsCreate

# Create router
router = APIRouter(
    prefix="/doctor",
    tags=["Doctor"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ DOCTOR SECTION
@router.get("/")
def doctor_section(request: Request, db: Session = Depends(get_db)):
    user = request.state.user

    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")

    db_user = db.query(models.User).filter(
        models.User.id == user["user_id"]
    ).first()

    return {
        "message": "Welcome Doctor!",
        "data": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "phone": db_user.phone,
            "hospital": db_user.hospital,
            "specialisation": db_user.specialisation,
            "qualification": db_user.qualification,
            "experience": db_user.experience,
            "referral_code": db_user.referral_code,

        }
    }

# ✅ DOCTOR MY PATIENTS
@router.get("/my-patients")
def get_my_patients(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user

    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")

    patients = db.query(models.User).filter(
        models.User.role == "patient"
    ).all()

    return [{
        "id": p.id,
        "name": p.name,
        "email": p.email,
        "phone": p.phone,
        "age": p.age,
        "gender": p.gender,
    } for p in patients]

# ✅ DOCTOR PATIENT THERAPY
@router.get("/patient-therapy/{patient_id}")
def get_patient_therapy(
    patient_id: int,
    duration: str = "7days",
    request: Request = None,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")

    days = 7 if duration == "7days" else 30 if duration == "1month" else 180

    start_date = datetime.utcnow() - timedelta(days=days)

    data = db.query(models.TherapyData).filter(
        models.TherapyData.patient_id == patient_id,
        models.TherapyData.date >= start_date
    ).all()

    patient = db.query(models.User).filter(
        models.User.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return {
        "patient_name": patient.name,
        "patient_id": patient_id,
        "duration": duration,
        "therapy_records": data
    }

# ✅ MACHINE SETTINGS CREATE
@router.post("/machine-settings")
def create_machine_settings(
    settings: MachineSettingsCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can set settings")

    db.add(models.MachineSettings(
        patient_id=settings.patient_id,
        doctor_id=current_user["user_id"],
        therapy_mode=settings.therapy_mode,
        min_pressure=settings.min_pressure,
        max_pressure=settings.max_pressure,
        start_pressure=settings.start_pressure,
        ramp_duration=settings.ramp_duration,
        pressure_off=settings.pressure_off,
    ))

    db.commit()

    return {"message": "Machine settings saved successfully!"}

# ✅ GET MACHINE SETTINGS
@router.get("/machine-settings/{patient_id}")
def get_machine_settings(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    settings = db.query(models.MachineSettings).filter(
        models.MachineSettings.patient_id == patient_id
    ).first()

    if not settings:
        raise HTTPException(status_code=404, detail="No settings found")

    return settings

# ✅ UPDATE MACHINE SETTINGS
@router.put("/machine-settings/{patient_id}")
def update_machine_settings(
    patient_id: int,
    settings: MachineSettingsCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can update")

    db_settings = db.query(models.MachineSettings).filter(
        models.MachineSettings.patient_id == patient_id
    ).first()

    if not db_settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    db_settings.therapy_mode = settings.therapy_mode
    db_settings.min_pressure = settings.min_pressure
    db_settings.max_pressure = settings.max_pressure
    db_settings.start_pressure = settings.start_pressure
    db_settings.ramp_duration = settings.ramp_duration
    db_settings.pressure_off = settings.pressure_off
    db_settings.updated_at = datetime.utcnow()

    db.commit()

    return {"message": "Machine settings updated successfully!"}

# ✅ DOCTOR DOWNLOAD PATIENT PDF
@router.get("/download-pdf/{therapy_id}")
def doctor_download_pdf(
    therapy_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Access denied")

    data = db.query(models.TherapyData).filter(
        models.TherapyData.id == therapy_id
    ).first()

    if not data:
        raise HTTPException(status_code=404, detail="Therapy record not found")

    file_path = f"uploads/{data.pdf_filename}"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file missing")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=data.pdf_filename
    )