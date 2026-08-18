from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from core.database import Base
from datetime import datetime

class TherapyData(Base):
    __tablename__ = "therapy_data"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
    compliance = Column(Float, nullable=True)
    usage_time = Column(Float, nullable=True)
    ahi_index = Column(Float, nullable=True)
    avg_pressure = Column(Float, nullable=True)
    leak_rate = Column(Float, nullable=True)
    duration_type = Column(String, nullable=True)
    pdf_filename = Column(String, nullable=True)

class MachineSettings(Base):
    __tablename__ = "machine_settings"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    doctor_id = Column(Integer)
    therapy_mode = Column(String, default="Auto CPAP")
    min_pressure = Column(Float, default=4.0)
    max_pressure = Column(Float, default=15.0)
    start_pressure = Column(Float, default=4.0)
    ramp_duration = Column(Integer, default=20)
    pressure_off = Column(Float, default=2.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class PdfReportData(Base):
    __tablename__ = "pdf_report_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    user_role = Column(String, default="patient")
    app_user_name = Column(String, nullable=True)
    app_user_email = Column(String, nullable=True)
    patient_details = Column(Text, nullable=True)
    total_days = Column(Integer, nullable=True)
    clinical_logs = Column(Text, nullable=True)
    pdf_base64 = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
