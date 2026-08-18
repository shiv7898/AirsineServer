from pydantic import BaseModel

class ReferralCreate(BaseModel):
    code: str
    role: str
    discount_percent: float
