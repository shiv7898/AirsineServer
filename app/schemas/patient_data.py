from pydantic import BaseModel
from typing import Optional

class TherapyCreate(BaseModel):
    compliance: Optional[float] = None
    usage_time: Optional[float] = None
    ahi_index: Optional[float] = None
    avg_pressure: Optional[float] = None
    leak_rate: Optional[float] = None
    duration_type: Optional[str] = None

class MachineSettingsCreate(BaseModel):
    patient_id: int
    therapy_mode: str = "Auto CPAP"
    min_pressure: float = 4.0
    max_pressure: float = 15.0
    start_pressure: float = 4.0
    ramp_duration: int = 20
    pressure_off: float = 2.0
