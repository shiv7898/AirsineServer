from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from database import Base
from datetime import datetime

class SupportQuery(Base):
    __tablename__ = "support_queries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    query_type = Column(String)
    message = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    image = Column(String, nullable=True)
