"""
services/password_reset_service.py

Centralized business logic for modern, secure password recovery.
Coordinates OTP generation, validation, rate limiting, and password updates
across all user types (Patient, Doctor, Distributor, AdminStaff, SuperAdmin).
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

import models
from core.config import settings
from core.security import hash_password
from core.exceptions import ValidationException, NotFoundException, DatabaseException
from helpers.validators import validate_email, validate_password
from services.user_service import UserService
from services.email_service import EmailService
from schemas.password_reset import ResetPasswordRequest


class PasswordResetService:
    """Service providing end-to-end password recovery workflows."""

    @staticmethod
    def request_password_reset(
        db: Session,
        email: str,
        background_tasks: BackgroundTasks
    ) -> dict:
        """
        Initiate password recovery for a user.
        Generates a 6-digit OTP and reset token, saves them in the database,
        and dispatches an email notification via background tasks.
        """
        validated_email = validate_email(email)

        # Find user across all role tables
        user = UserService.find_user_by_email(db, validated_email)
        if not user:
            raise NotFoundException(
                "No registered account found with this email address. Please check your email or register."
            )

        try:
            # Invalidate any previously issued active OTPs for this email
            active_resets = db.query(models.PasswordReset).filter(
                models.PasswordReset.email == validated_email,
                models.PasswordReset.is_used == False
            ).all()
            for record in active_resets:
                record.is_used = True

            # Generate a cryptographically secure 6-digit OTP
            otp = f"{secrets.randbelow(900000) + 100000}"
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

            # Persist reset record
            new_reset = models.PasswordReset(
                email=validated_email,
                otp=otp,
                reset_token=reset_token,
                user_role=getattr(user, "role", "user"),
                user_id=getattr(user, "id", None),
                attempts=0,
                max_attempts=5,
                is_used=False,
                expires_at=expires_at,
            )
            db.add(new_reset)
            db.commit()
            db.refresh(new_reset)

            # Dispatch modern HTML email asynchronously
            user_name = getattr(user, "name", "Valued User")
            background_tasks.add_task(
                EmailService.send_password_reset_email,
                to_email=validated_email,
                user_name=user_name,
                otp=otp,
                reset_token=reset_token
            )

            return {
                "success": True,
                "message": "A 6-digit verification code has been sent to your email address.",
                "email": validated_email,
            }

        except (ValidationException, NotFoundException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to initiate password reset: {str(e)}")

    @staticmethod
    def verify_otp(db: Session, email: str, otp: str) -> dict:
        """
        Verify the 6-digit OTP code submitted by the user.
        Returns a single-use reset_token to be used in the reset step.
        """
        validated_email = validate_email(email)
        clean_otp = str(otp).strip()

        # Query latest active reset entry
        reset_record = db.query(models.PasswordReset).filter(
            models.PasswordReset.email == validated_email,
            models.PasswordReset.is_used == False
        ).order_by(models.PasswordReset.created_at.desc()).first()

        if not reset_record:
            raise ValidationException(
                "No active password reset request found. Please request a new code.",
                field="otp"
            )

        if reset_record.is_expired:
            reset_record.is_used = True
            db.commit()
            raise ValidationException(
                "The verification code has expired. Please request a new one.",
                field="otp"
            )

        if reset_record.attempts >= reset_record.max_attempts:
            reset_record.is_used = True
            db.commit()
            raise ValidationException(
                "Maximum verification attempts exceeded. Please request a new code.",
                field="otp"
            )

        # Check OTP match
        if reset_record.otp != clean_otp:
            reset_record.attempts += 1
            db.commit()
            remaining = reset_record.max_attempts - reset_record.attempts
            raise ValidationException(
                f"Invalid verification code. {remaining} attempt(s) remaining.",
                field="otp"
            )

        return {
            "success": True,
            "message": "Verification code confirmed successfully.",
            "email": validated_email,
            "reset_token": reset_record.reset_token,
        }

    @staticmethod
    def reset_password(
        db: Session,
        payload: ResetPasswordRequest,
        background_tasks: BackgroundTasks
    ) -> dict:
        """
        Finalize password reset.
        Accepts either verified reset_token or direct email + otp combination.
        """
        if payload.new_password != payload.confirm_password:
            raise ValidationException("Passwords do not match.", field="confirm_password")

        validated_password = validate_password(payload.new_password)

        reset_record: Optional[models.PasswordReset] = None

        # Scenario 1: Using reset_token returned from verify_otp
        if payload.reset_token and payload.reset_token.strip():
            reset_record = db.query(models.PasswordReset).filter(
                models.PasswordReset.reset_token == payload.reset_token.strip(),
                models.PasswordReset.is_used == False
            ).first()

        # Scenario 2: Direct email + OTP verification
        elif payload.email and payload.otp:
            validated_email = validate_email(payload.email)
            clean_otp = str(payload.otp).strip()
            reset_record = db.query(models.PasswordReset).filter(
                models.PasswordReset.email == validated_email,
                models.PasswordReset.otp == clean_otp,
                models.PasswordReset.is_used == False
            ).order_by(models.PasswordReset.created_at.desc()).first()

        else:
            raise ValidationException(
                "Please provide either a verified reset_token or your email and OTP code."
            )

        if not reset_record or not reset_record.is_valid:
            raise ValidationException(
                "Invalid or expired reset session. Please request a new verification code."
            )

        # Find the user record across all user models
        user = UserService.find_user_by_email(db, reset_record.email)
        if not user:
            raise NotFoundException("User account associated with this request was not found.")

        try:
            # Hash new password securely and persist
            user.password = hash_password(validated_password)
            reset_record.is_used = True
            db.commit()
            db.refresh(user)

            # Send confirmation email alert in background
            user_name = getattr(user, "name", "Valued User")
            background_tasks.add_task(
                EmailService.send_password_changed_notification,
                to_email=user.email,
                user_name=user_name
            )

            return {
                "success": True,
                "message": "Your password has been reset successfully. You can now log in with your new password.",
                "email": user.email,
            }

        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to reset password: {str(e)}")

    @staticmethod
    def resend_otp(
        db: Session,
        email: str,
        background_tasks: BackgroundTasks
    ) -> dict:
        """
        Resend a fresh OTP with rate-limiting cooldown protection.
        """
        validated_email = validate_email(email)

        # Check rate-limiting cooldown (60 seconds)
        last_request = db.query(models.PasswordReset).filter(
            models.PasswordReset.email == validated_email,
            models.PasswordReset.is_used == False
        ).order_by(models.PasswordReset.created_at.desc()).first()

        if last_request and (datetime.utcnow() - last_request.created_at).total_seconds() < 60:
            remaining_seconds = int(60 - (datetime.utcnow() - last_request.created_at).total_seconds())
            raise ValidationException(
                f"Please wait {remaining_seconds} seconds before requesting a new code.",
                field="email"
            )

        return PasswordResetService.request_password_reset(
            db=db,
            email=validated_email,
            background_tasks=background_tasks
        )
