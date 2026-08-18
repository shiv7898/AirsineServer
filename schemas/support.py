from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupportQueryCreate(BaseModel):
    category: str
    message: str

class SupportQueryResponse(BaseModel):
    id: int
    user_id: int
    query_type: str
    message: str
    status: str
    created_at: datetime
    image: Optional[str] = None
    resolution_message: Optional[str] = None
    resolved_at: Optional[datetime] = None

class SupportQueryResolve(BaseModel):
    resolution_message: Optional[str] = None
    
    class Config:
        from_attributes = True
