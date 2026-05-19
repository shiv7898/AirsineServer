from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from datetime import datetime
import models
import os

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

# Database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ GENERATE THERAPY REPORT PDF
@router.get("/therapy/{patient_id}")
def generate_therapy_report(
    patient_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = request.state.user

    # Only doctor or patient
    if current_user["role"] not in ["doctor", "patient"]:
        raise HTTPException(status_code=403, detail="Access denied")

    patient = db.query(models.User).filter(
        models.User.id == patient_id
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    therapy_data = db.query(models.TherapyData).filter(
        models.TherapyData.patient_id == patient_id
    ).all()

    if not therapy_data:
        raise HTTPException(status_code=404, detail="No therapy data found")

    # Create reports folder
    os.makedirs("reports", exist_ok=True)

    filename = f"therapy_report_{patient_id}.pdf"
    filepath = f"reports/{filename}"

    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("CPAP Therapy Report", styles['Title']))
    elements.append(Spacer(1, 20))

    # Patient info
    elements.append(Paragraph(f"Patient Name: {patient.name}", styles['BodyText']))
    elements.append(Paragraph(f"Patient ID: {patient.id}", styles['BodyText']))
    elements.append(Paragraph(f"Generated: {datetime.utcnow()}", styles['BodyText']))
    elements.append(Spacer(1, 20))

    # Therapy records
    for t in therapy_data:
        elements.append(Paragraph(
            f"""
            <b>Date:</b> {t.date}<br/>
            <b>Compliance:</b> {t.compliance}%<br/>
            <b>Usage Time:</b> {t.usage_time} hrs<br/>
            <b>AHI Index:</b> {t.ahi_index}<br/>
            <b>Average Pressure:</b> {t.avg_pressure}<br/>
            <b>Leak Rate:</b> {t.leak_rate}<br/>
            """,
            styles['BodyText']
        ))
        elements.append(Spacer(1, 15))

    # Build PDF
    doc.build(elements)

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename
    )