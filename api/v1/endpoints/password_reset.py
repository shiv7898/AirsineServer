"""
api/v1/endpoints/password_reset.py

Modern, secure Password Reset and Recovery endpoints.
Supports email-based password recovery for all registered user roles
(Patients, Doctors, Distributors, Admin Staff, and Super Admins).
"""
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session

from core.database import SessionLocal
from schemas.password_reset import (
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
    ResendOtpRequest,
    PasswordResetResponse,
)
from services.password_reset_service import PasswordResetService

router = APIRouter(tags=["Password Reset"])


def get_db():
    """Database session dependency for password reset endpoints."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset OTP",
    description="Sends a 6-digit one-time verification code to the registered email address."
)
def forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Step 1: User provides registered email ID.
    System generates a secure 6-digit OTP and delivers it via email.
    """
    return PasswordResetService.request_password_reset(
        db=db,
        email=payload.email,
        background_tasks=background_tasks
    )


@router.post(
    "/verify-otp",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify Password Reset OTP",
    description="Verifies the 6-digit code received via email and issues a temporary reset token."
)
def verify_otp(
    payload: VerifyOtpRequest,
    db: Session = Depends(get_db),
):
    """
    Step 2: User submits email and 6-digit OTP.
    Returns a secure reset_token to authorize setting the new password.
    """
    return PasswordResetService.verify_otp(
        db=db,
        email=payload.email,
        otp=payload.otp
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset User Password",
    description="Updates the user's password using either the verified reset_token or direct (email + OTP)."
)
def reset_password(
    payload: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Step 3: User submits new password along with reset_token (or email + OTP).
    The password is encrypted, updated in the database, and an alert email is sent.
    """
    return PasswordResetService.reset_password(
        db=db,
        payload=payload,
        background_tasks=background_tasks
    )


@router.post(
    "/resend-otp",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend Password Reset OTP",
    description="Resends a fresh OTP code to the registered email address with cooldown protection."
)
def resend_otp(
    payload: ResendOtpRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Resend verification code to user's registered email with a 60-second cooldown.
    """
    return PasswordResetService.resend_otp(
        db=db,
        email=payload.email,
        background_tasks=background_tasks
    )
