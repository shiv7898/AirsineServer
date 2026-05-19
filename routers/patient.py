from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from schemas import UserCreate, TherapyCreate, SupportQueryCreate
from datetime import datetime, timedelta
import shutil
import os
import pdfplumber
import re
from fastapi.responses import Response
from xhtml2pdf import pisa
import io

# Create router
router = APIRouter(
    prefix="/patient",
    tags=["Patient"]
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function - PDF text extraction
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:  
            text += page.extract_text() or ""
    return text

# Helper function - Parse therapy data
def parse_therapy_data(text):
    match = re.search(
        r"(\d+\.?\d*)h\s+(\d+\.?\d*)%\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)",
        text
    )
    if match:
        data = {
            "usage_time": match.group(1),
            "compliance": match.group(2),
            "ahi_index": match.group(3),
            "avg_pressure": match.group(4),
            "leak_rate": match.group(5),
        }
        print("===== PARSED DATA =====")
        print(data)
        return data
    print("===== NO MATCH FOUND =====")
    return {
        "usage_time": None,
        "compliance": None,
        "ahi_index": None,
        "avg_pressure": None,
        "leak_rate": None,
    }

# PATIENT SECTION
@router.get("/")
def patient_section(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    db_user = db.query(models.User).filter(models.User.id == user["user_id"]).first()
    return {
        "message": "Welcome Patient!",
        "data": {
            "id": db_user.id, "name": db_user.name,
            "email": db_user.email, "phone": db_user.phone,
            "home_address": db_user.home_address, "district": db_user.district,
            "state": db_user.state, "pincode": db_user.pincode,
        }
    }

# GET PROFILE
@router.get("/profile")
def get_profile(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    db_user = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "role": db_user.role,
        "phone": db_user.phone,
        "gender": db_user.gender,
        "age": db_user.age,
        "dob": db_user.dob,
        "home_address": db_user.home_address,
        "area": db_user.area,
        "district": db_user.district,
        "state": db_user.state,
        "pincode": db_user.pincode,
        "hospital": db_user.hospital,
        "specialisation": db_user.specialisation,
        "qualification": db_user.qualification,
        "experience": db_user.experience,
        "company_name": db_user.company_name,
        "business_type": db_user.business_type,
        "distributor_type": db_user.distributor_type,
        "license_number": db_user.license_number,
        "referral_code": db_user.referral_code,
    }

# UPDATE PROFILE
@router.put("/profile")
def update_profile(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user
        db_user = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        db_user.name = user.name
        db_user.phone = user.phone
        db_user.gender = user.gender
        db_user.age = user.age
        db_user.dob = user.dob
        db_user.home_address = user.homeAddress
        db_user.area = user.area
        db_user.district = user.district
        db_user.state = user.state
        db_user.pincode = user.pincode
        db_user.hospital = user.hospital
        db_user.specialisation = user.specialisation
        db_user.qualification = user.qualification
        db_user.experience = user.experience
        db_user.company_name = user.companyName
        db_user.business_type = user.businessType
        db_user.distributor_type = user.distributorType
        db_user.license_number = user.licenseNumber
        db.commit()
        db.refresh(db_user)
        return {"message": "Profile updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SAVE THERAPY DATA
@router.post("/therapy")
def save_therapy(therapy: TherapyCreate, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user
        if current_user["role"] != "patient":
            raise HTTPException(status_code=403, detail="Only patients can save therapy data")
        new_therapy = models.TherapyData(
            patient_id=current_user["user_id"],
            compliance=therapy.compliance, usage_time=therapy.usage_time,
            ahi_index=therapy.ahi_index, avg_pressure=therapy.avg_pressure,
            leak_rate=therapy.leak_rate, duration_type=therapy.duration_type,
        )
        db.add(new_therapy)
        db.commit()
        if therapy.compliance and therapy.compliance < 50:
            db.add(models.Notification(
                user_id=current_user["user_id"],
                title="Low Compliance Alert!",
                message=f"Your compliance dropped to {therapy.compliance}%! Please use your CPAP regularly."
            ))
            db.commit()
        return {"message": "Therapy data saved successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET THERAPY DATA
@router.get("/therapy-data")
def get_therapy_data(duration: str = "7days", request: Request = None, db: Session = Depends(get_db)):
    current_user = request.state.user
    days = 7 if duration == "7days" else 30 if duration == "1month" else 180
    start_date = datetime.utcnow() - timedelta(days=days)
    return db.query(models.TherapyData).filter(
        models.TherapyData.patient_id == current_user["user_id"],
        models.TherapyData.date >= start_date).all()

import json
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PdfSyncPayload(BaseModel):
    app_user_name: Optional[str] = None
    app_user_email: Optional[str] = None
    patient_details: Optional[Dict[str, Any]] = None
    total_days: Optional[int] = None
    clinical_logs: Optional[List[Dict[str, Any]]] = None

# SYNC PDF DATA (Dummy Endpoint)
@router.post("/sync-pdf-data")
async def sync_pdf_data(payload: PdfSyncPayload, request: Request, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user
        
        # Save payload to database
        report_data = models.PdfReportData(
            user_id=current_user["user_id"],
            app_user_name=payload.app_user_name,
            app_user_email=payload.app_user_email,
            patient_details=json.dumps(payload.patient_details or {}),
            total_days=payload.total_days,
            clinical_logs=json.dumps(payload.clinical_logs or [])
        )
        db.add(report_data)
        db.commit()
        
        print("====== RECEIVED & SAVED SYNC DATA ======")
        print(f"User: {payload.app_user_name}")
        print(f"Total Days: {payload.total_days}")
        print("========================================")
        
        return {"message": "Data synced to database successfully", "received_days": payload.total_days}
    except Exception as e:
        print(f"Sync DB Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# GET SYNCED PDF HISTORY
@router.get("/synced-pdf-history")
def get_synced_pdf_history(request: Request = None, db: Session = Depends(get_db)):
    current_user = request.state.user
    reports = db.query(models.PdfReportData).filter(
        models.PdfReportData.user_id == current_user["user_id"]
    ).order_by(models.PdfReportData.id.desc()).all()
    
    result = []
    for r in reports:
        patient_name = r.app_user_name
        try:
            if r.patient_details:
                details = json.loads(r.patient_details)
                if isinstance(details, dict) and "name" in details:
                    patient_name = details["name"]
        except:
            pass
            
        result.append({
            "id": r.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "total_days": r.total_days,
            "patient_name": patient_name or "Unknown"
        })
    return result

# DOWNLOAD SYNCED PDF DATA
@router.get("/download-synced-pdf")
def download_synced_pdf(days: int = 7, report_id: int = None, request: Request = None, db: Session = Depends(get_db)):
    current_user = request.state.user
    
    if report_id:
        report_data = db.query(models.PdfReportData).filter(
            models.PdfReportData.id == report_id,
            models.PdfReportData.user_id == current_user["user_id"]
        ).first()
    else:
        # Get the latest synced pdf data for this user
        report_data = db.query(models.PdfReportData).filter(
            models.PdfReportData.user_id == current_user["user_id"]
        ).order_by(models.PdfReportData.id.desc()).first()
    
    if not report_data:
        raise HTTPException(status_code=404, detail="No synced data found. Please sync from app first.")
        
    clinical_logs = json.loads(report_data.clinical_logs) if report_data.clinical_logs else []
    
    # Filter logs by days
    filtered_logs = clinical_logs[:days]
    
    patient_details = json.loads(report_data.patient_details) if report_data.patient_details else {}
    
    table_rows = ""
    for idx, log in enumerate(filtered_logs):
        row_bg = "#FFFFFF" if idx % 2 == 0 else "#F3F8FF"
        ahi_color = "#D32F2F" if float(log.get("ahi", 0)) > 5 else "#1E7E34"
        
        usage = str(log.get("usage_hours", "0"))
        if len(usage) > 4: usage = usage[:4]
        is_compliant = float(usage) >= 4 if usage.replace('.','',1).isdigit() else False
        usage_badge = '<span style="color:#2E7D32;">&ge;4h</span>' if is_compliant else '<span style="color:#E65100;">&lt;4h</span>'
        
        table_rows += f"""
        <tr style="background:{row_bg};">
            <td>{log.get("date", "--")}</td>
            <td>{usage} {usage_badge}</td>
            <td>{log.get("therapy_type", "CPAP")}</td>
            <td>{log.get("pressure_avg", "0")}</td>
            <td>{log.get("avg_flow", "0")}</td>
            <td>{log.get("leak_rate", "0")}</td>
            <td>{log.get("avg_resp_rate", "0")}</td>
            <td style="color:{ahi_color};font-weight:bold;">{log.get("ahi", "0")}</td>
            <td>{log.get("mask_fault_count", "0")}</td>
            <td>{log.get("low_pressure_count", "0")}</td>
        </tr>
        """
        
    date_str = datetime.utcnow().strftime('%d-%m-%Y')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
    @page {{ size: a4 portrait; margin: 1cm; }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:Helvetica, sans-serif; font-size:11px; color:#1a1a2e; background:#fff; }}
    .hdr-banner {{ background:#ffffff; border:2px solid #065F46; color:#065F46; padding:16px 22px; border-radius:10px; margin-bottom:18px; }}
    .hdr-banner h1 {{ font-size:20px; font-weight:bold; letter-spacing:1px; margin:0; }}
    .hdr-banner .hdr-sub {{ font-size:10px; margin-top:3px; color:#065F46; }}
    .sec-title {{ font-size:12px; font-weight:bold; color:#065F46; border-left:4px solid #10B981; padding-left:8px; margin-bottom:9px; margin-top:14px; }}
    .ig {{ width:100%; border-collapse:collapse; }}
    .ig td {{ padding:4px 7px; font-size:11px; }}
    .lbl {{ color:#374151; font-weight:bold; width:130px; }}
    .val {{ color:#1a1a2e; }}
    .hr-dash {{ border:none; border-top:1.5px dashed #34D399; margin:12px 0; }}
    .hr-blue {{ border:none; border-top:2px solid #10B981; margin:14px 0; }}
    .dt {{ width:100%; border-collapse:collapse; font-size:9.5px; margin-top:6px; }}
    .dt th {{ background:#065F46; color:#fff; padding:5px 3px; text-align:center; font-size:9px; border:1px solid #065F46; }}
    .dt td {{ border:1px solid #D1FAE5; padding:5px 3px; text-align:center; }}
    .sig-table {{ width: 100%; margin-top: 50px; text-align: center; }}
    .sig-line {{ border-top: 1px solid #333; width: 150px; margin: 0 auto; }}
    .page-break {{ pdf-page-break-before: always; }}
    .graph-box {{ border: 1px solid #D1FAE5; border-radius: 8px; padding: 15px; margin-bottom: 20px; text-align: center; background: #F9FAFB; }}
    .graph-title {{ font-size:12px; font-weight:bold; color:#065F46; margin-bottom: 10px; }}
    </style>
    </head>
    <body>
    <div class="hdr-banner">
        <table width="100%">
            <tr>
                <td width="50%">
                    <h1>Therapy Report</h1>
                    <div class="hdr-sub">Airsine CPAP Clinical Summary</div>
                </td>
                <td width="50%" align="right" style="font-size:10px;">
                    <b>Report Date:</b> {date_str}<br/>
                    <b>Total Days:</b> {len(filtered_logs)}<br/>
                    <b>Device:</b> {patient_details.get("machine_serial", "-")}
                </td>
            </tr>
        </table>
    </div>

    <div class="sec-title">Patient Details</div>
    <table class="ig">
        <tr>
            <td class="lbl">Patient ID:</td><td class="val">P-{patient_details.get("patient_custom_id", patient_details.get("id", "-"))}</td>
            <td class="lbl">Full Name:</td><td class="val">{patient_details.get("name", report_data.app_user_name)}</td>
        </tr>
        <tr>
            <td class="lbl">Gender:</td><td class="val">{patient_details.get("gender", "-")}</td>
            <td class="lbl">Date of Birth:</td><td class="val">{patient_details.get("dob", "-")}</td>
        </tr>
        <tr>
            <td class="lbl">Phone:</td><td class="val">{patient_details.get("phone", "-")}</td>
            <td class="lbl">Email:</td><td class="val">{patient_details.get("email", report_data.app_user_email)}</td>
        </tr>
    </table>

    <hr class="hr-dash"/>
    <div class="sec-title">Referring Physician</div>
    <table class="ig">
        <tr>
            <td class="lbl">Doctor Name:</td><td class="val">{patient_details.get("doctor_name", "-")}</td>
            <td class="lbl">Doctor Phone:</td><td class="val">{patient_details.get("doctor_phone", "-")}</td>
        </tr>
    </table>

    <hr class="hr-blue"/>

    <div class="sec-title">Daily Therapy Log</div>
    <table class="dt">
        <thead>
            <tr>
                <th>Date</th>
                <th>Usage (H:M)</th>
                <th>Mode</th>
                <th>Pressure<br/>(cmH2O)</th>
                <th>Flow<br/>(L/min)</th>
                <th>Leak<br/>(L/min)</th>
                <th>Resp<br/>Rate</th>
                <th>AHI</th>
                <th>Open<br/>Mask</th>
                <th>Low<br/>Press</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>

  

 
    </body>
    </html>
    """
    
    # Create PDF
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html_content), dest=buffer)
    
    if pisa_status.err:
        raise HTTPException(status_code=500, detail="Error generating PDF")
        
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=Airsine_Report_{days}days.pdf"
        }
    )

# PATIENT DASHBOARD
@router.get("/dashboard")
def patient_dashboard(duration: str = "7days", request: Request = None, db: Session = Depends(get_db)):
    current_user = request.state.user
    if current_user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Access denied")
    days = 7 if duration == "7days" else 30 if duration == "1month" else 180
    start_date = datetime.utcnow() - timedelta(days=days)
    data = db.query(models.TherapyData).filter(
        models.TherapyData.patient_id == current_user["user_id"],
        models.TherapyData.date >= start_date).all()
    if not data:
        return {"message": "No therapy data found", "duration": duration}
    valid_compliance = [d.compliance for d in data if d.compliance is not None]
    valid_usage = [d.usage_time for d in data if d.usage_time is not None]
    valid_ahi = [d.ahi_index for d in data if d.ahi_index is not None]
    valid_pressure = [d.avg_pressure for d in data if d.avg_pressure is not None]
    valid_leak = [d.leak_rate for d in data if d.leak_rate is not None]
    return {
        "duration": duration,
        "total_records": len(data),
        "compliance_percent": round(sum(valid_compliance) / len(valid_compliance), 1) if valid_compliance else 0,
        "usage_time_hrs": round(sum(valid_usage) / len(valid_usage), 1) if valid_usage else 0,
        "ahi_index": round(sum(valid_ahi) / len(valid_ahi), 1) if valid_ahi else 0,
        "avg_pressure_cm": round(sum(valid_pressure) / len(valid_pressure), 1) if valid_pressure else 0,
        "leak_rate_lm": round(sum(valid_leak) / len(valid_leak), 1) if valid_leak else 0,
    }

# UPLOAD PDF
@router.post("/upload-pdf")
def upload_pdf(file: UploadFile = File(...), request: Request = None, db: Session = Depends(get_db)):
    try:
        current_user = request.state.user
        if current_user["role"] != "patient":
            raise HTTPException(status_code=403, detail="Only patients can upload PDF")
        os.makedirs("uploads", exist_ok=True)
        filename = f"patient_{current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
        with open(f"uploads/{filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_path = f"uploads/{filename}"
        text = extract_text_from_pdf(file_path)
        print("===== PDF TEXT =====")
        print(text)
        data = parse_therapy_data(text)
        print("===== DATA BEFORE CONVERSION =====")
        print(data)
        new_data = models.TherapyData(
            patient_id=current_user["user_id"],
            pdf_filename=filename,
            usage_time=float(data["usage_time"]) if data["usage_time"] else None,
            compliance=float(data["compliance"]) if data["compliance"] else None,
            ahi_index=float(data["ahi_index"]) if data["ahi_index"] else None,
            avg_pressure=float(data["avg_pressure"]) if data["avg_pressure"] else None,
            leak_rate=float(data["leak_rate"]) if data["leak_rate"] else None
        )
        print("===== DATA AFTER CONVERSION =====")
        print(f"usage_time: {new_data.usage_time}")
        print(f"compliance: {new_data.compliance}")
        print(f"ahi_index: {new_data.ahi_index}")
        print(f"avg_pressure: {new_data.avg_pressure}")
        print(f"leak_rate: {new_data.leak_rate}")
        db.add(new_data)
        db.commit()
        return {"message": "PDF uploaded successfully!", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DOWNLOAD PDF
@router.get("/download-pdf/{therapy_id}")
def download_pdf(therapy_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    data = db.query(models.TherapyData).filter(
        models.TherapyData.id == therapy_id,
        models.TherapyData.patient_id == current_user["user_id"]
    ).first()
    if not data:
        raise HTTPException(status_code=404, detail="Therapy record not found")
    file_path = f"uploads/{data.pdf_filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF file missing on server")
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=data.pdf_filename
    )

# GET NOTIFICATIONS
@router.get("/notifications")
def get_notifications(request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    return db.query(models.Notification).filter(
        models.Notification.user_id == current_user["user_id"]).all()

# READ NOTIFICATION
@router.put("/notifications/{notification_id}")
def read_notification(notification_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = request.state.user
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user["user_id"]).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    db.commit()
    return {"message": "Marked as read!"}

# SUPPORT QUERY
@router.post("/support-query")
def support_query(
    request: Request,
    category: str = Form(...),
    message: str = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    current_user = request.state.user
    
    # Fetch user details
    user_db = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    image_filename = None
    os.makedirs("uploads/support", exist_ok=True)

    if image:
        extension = image.filename.split(".")[-1]
        image_filename = f"pat_{current_user['user_id']}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{extension}"
        image_path = f"uploads/support/{image_filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    new_query = models.Notification(
        user_id=current_user["user_id"],
        title=f"Support Query - {category}",
        message=message,
        image=image_filename,
        user_name=user_db.name,
        user_email=user_db.email,
        user_role=user_db.role,
        is_read=False
    )
    db.add(new_query)
    db.commit()
    return {"message": "Query submitted! We will respond within 24 hours."}