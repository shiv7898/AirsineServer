from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from database import Base
from datetime import datetime

class Notification(Base):
    __tablename__ = "users_support_query"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    title = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    image = Column(String, nullable=True)
    user_name = Column(String, nullable=True)
    user_email = Column(String, nullable=True)
    user_role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
