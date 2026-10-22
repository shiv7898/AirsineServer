"""
web/controllers/password_reset.py

Dedicated controller for Web Admin and Sub-Admin Password Reset workflows.
Enforces role-based checks so only administrative staff (super_admin, admin, sub_admin)
can reset credentials via the web management portal.
"""
from fastapi import APIRouter, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session

from core.database import SessionLocal
from core.exceptions import AuthenticationException, NotFoundException
from services.user_service import UserService
from services.password_reset_service import PasswordResetService
from helpers.validators import validate_email
from schemas.password_reset import (
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
    ResendOtpRequest,
    PasswordResetResponse,
)

router = APIRouter(tags=["Web Password Reset"])

ALLOWED_ADMIN_ROLES = ["super_admin", "admin", "sub_admin"]


def get_db():
    """Database session dependency for web password reset."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_admin_user(db: Session, email: str):
    """
    Verify that the user exists and holds an administrative role
    (super_admin, admin, or sub_admin).
    """
    validated_email = validate_email(email)
    user = UserService.find_user_by_email(db, validated_email)

    if not user:
        raise NotFoundException(
            "No account found with this email. Please verify your administrative email address."
        )

    user_role = getattr(user, "role", "")
    if user_role not in ALLOWED_ADMIN_ROLES:
        raise AuthenticationException(
            f"Access restricted: '{user_role.title()}' accounts cannot reset password via the Admin Portal. "
            "Please use the Airsine mobile application."
        )

    return user, validated_email


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Web Admin Request Password Reset OTP",
    description="Sends a 6-digit OTP code to the registered administrator email address."
)
def web_forgot_password(
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Step 1: Admin or Sub-Admin enters their email.
    Validates administrative role and dispatches verification OTP.
    """
    user, validated_email = _ensure_admin_user(db, payload.email)

    return PasswordResetService.request_password_reset(
        db=db,
        email=validated_email,
        background_tasks=background_tasks
    )


@router.post(
    "/verify-otp",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Web Admin Verify OTP",
    description="Verifies the 6-digit code received by the administrator."
)
def web_verify_otp(
    payload: VerifyOtpRequest,
    db: Session = Depends(get_db),
):
    """
    Step 2: Admin submits email + 6-digit OTP.
    Validates administrative role and returns a secure reset_token.
    """
    _ensure_admin_user(db, payload.email)

    return PasswordResetService.verify_otp(
        db=db,
        email=payload.email,
        otp=payload.otp
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Web Admin Set New Password",
    description="Resets the administrative account password with new and confirm password."
)
def web_reset_password(
    payload: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Step 3: Admin sets a new password using either verified reset_token or direct (email + OTP).
    Validates role and updates the user's password securely.
    """
    if payload.email:
        _ensure_admin_user(db, payload.email)

    return PasswordResetService.reset_password(
        db=db,
        payload=payload,
        background_tasks=background_tasks
    )


@router.post(
    "/resend-otp",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Web Admin Resend OTP",
    description="Resends a fresh verification OTP to the administrator's email with cooldown."
)
def web_resend_otp(
    payload: ResendOtpRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Resend verification code to admin with 60-second cooldown protection.
    """
    _ensure_admin_user(db, payload.email)

    return PasswordResetService.resend_otp(
        db=db,
        email=payload.email,
        background_tasks=background_tasks
    )
