"""
schemas/password_reset.py

Pydantic schemas for password recovery, OTP verification, and password updates.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Registered email address")


class VerifyOtpRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    otp: str = Field(..., min_length=4, max_length=10, description="6-digit verification code received via email")


class ResetPasswordRequest(BaseModel):
    email: Optional[str] = Field(None, description="Registered email address (required if reset_token is not provided)")
    otp: Optional[str] = Field(None, description="6-digit OTP code (required if reset_token is not provided)")
    reset_token: Optional[str] = Field(None, description="Verified reset token received from /verify-otp")
    new_password: str = Field(..., min_length=6, max_length=28, description="New secure password")
    confirm_password: str = Field(..., min_length=6, max_length=28, description="Confirm new password")


class ResendOtpRequest(BaseModel):
    email: str = Field(..., description="Registered email address")


class PasswordResetResponse(BaseModel):
    success: bool = True
    message: str
    email: Optional[str] = None
    reset_token: Optional[str] = None

    class Config:
        from_attributes = True
