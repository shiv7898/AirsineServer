"""
models/password_reset.py

SQLAlchemy model for password reset requests and OTP management.
Stores secure verification codes and short-lived reset tokens.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from core.database import Base


class PasswordReset(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), index=True, nullable=False)
    otp = Column(String(10), nullable=False)
    reset_token = Column(String(255), unique=True, index=True, nullable=True)
    user_role = Column(String(50), nullable=True)
    user_id = Column(Integer, nullable=True)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    @property
    def is_expired(self) -> bool:
        """Check if OTP / reset token has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if reset record is active, unused, and within attempt limits."""
        return (not self.is_used) and (not self.is_expired) and (self.attempts < self.max_attempts)
