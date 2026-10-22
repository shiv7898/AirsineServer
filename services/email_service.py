"""
services/email_service.py

Modern email delivery service for Airsine Healthcare API.
Handles HTML and plain-text email formatting, SMTP delivery with dual-port
fallback (Port 587 STARTTLS <-> Port 465 SSL), dynamic env reloading,
and helpful development-mode diagnostics.
"""
import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv
from core.config import settings, reload_environment

logger = logging.getLogger("airsine.email")


class EmailService:
    """Service handling transactional and security emails."""

    @staticmethod
    def _create_reset_email_html(user_name: str, otp: str, expire_minutes: int) -> str:
        """Generate a modern, responsive HTML email template for password reset."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Password Reset - Airsine Healthcare</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #F8FAFC; color: #1E293B;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #F8FAFC; padding: 40px 15px;">
    <tr>
      <td align="center">
        <!-- Main Card -->
        <table role="presentation" width="100%" style="max-width: 540px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01); border: 1px solid #E2E8F0;">
          
          <!-- Header Banner -->
          <tr>
            <td style="background: linear-gradient(135deg, #0D9488 0%, #10B981 100%); padding: 32px 30px; text-align: center;">
              <h1 style="margin: 0; font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: 1.5px; text-transform: uppercase;">
                AIRSINE HEALTHCARE
              </h1>
              <p style="margin: 6px 0 0; color: rgba(255, 255, 255, 0.9); font-size: 13px; font-weight: 500; letter-spacing: 0.5px;">
                Secure Medical Account Services
              </p>
            </td>
          </tr>

          <!-- Body Content -->
          <tr>
            <td style="padding: 36px 32px 24px;">
              <h2 style="margin: 0 0 12px; font-size: 20px; font-weight: 700; color: #0F172A;">
                Password Reset Verification
              </h2>
              <p style="margin: 0 0 20px; font-size: 15px; line-height: 1.6; color: #475569;">
                Hello <strong>{user_name}</strong>,
              </p>
              <p style="margin: 0 0 24px; font-size: 15px; line-height: 1.6; color: #475569;">
                We received a request to reset your password for your Airsine account. Use the one-time verification code (OTP) below to complete your reset request:
              </p>

              <!-- OTP Callout Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 28px 0;">
                <tr>
                  <td align="center" style="background-color: #F0FDF4; border: 2px dashed #86EFAC; border-radius: 12px; padding: 22px;">
                    <span style="display: block; font-size: 12px; font-weight: 700; color: #15803D; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px;">
                      Your Verification Code
                    </span>
                    <span style="display: block; font-family: 'Courier New', Courier, monospace; font-size: 34px; font-weight: 800; color: #065F46; letter-spacing: 8px;">
                      {otp}
                    </span>
                    <span style="display: block; font-size: 12px; color: #16A34A; margin-top: 6px; font-weight: 600;">
                      ⏱ Expires in {expire_minutes} minutes
                    </span>
                  </td>
                </tr>
              </table>

              <!-- Notice -->
              <p style="margin: 0 0 16px; font-size: 14px; line-height: 1.6; color: #64748B;">
                Enter this code in your mobile app or web portal to choose a new password. For security reasons, do <strong>not</strong> share this code with anyone. Airsine representatives will never ask for your verification code.
              </p>

              <!-- Warning Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-top: 24px;">
                <tr>
                  <td style="background-color: #FFFBEB; border-left: 4px solid #F59E0B; border-radius: 6px; padding: 12px 16px;">
                    <p style="margin: 0; font-size: 13px; color: #B45309; line-height: 1.5;">
                      <strong>Didn't request this?</strong> If you did not make this request, your account is still secure. You can safely ignore this email.
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 24px 32px; text-align: center;">
              <p style="margin: 0; font-size: 12px; color: #94A3B8; line-height: 1.5;">
                &copy; Airsine Healthcare Systems. All rights reserved.<br>
                This is an automated system email. Please do not reply directly.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    @staticmethod
    def _create_password_changed_html(user_name: str) -> str:
        """Generate HTML email notifying that the user's password was changed."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Security Alert: Password Changed - Airsine</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #F8FAFC; color: #1E293B;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #F8FAFC; padding: 40px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 540px; background-color: #FFFFFF; border-radius: 16px; overflow: hidden; border: 1px solid #E2E8F0;">
          <tr>
            <td style="background: linear-gradient(135deg, #0D9488 0%, #10B981 100%); padding: 24px 30px; text-align: center;">
              <h1 style="margin: 0; font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: 1px;">
                AIRSINE HEALTHCARE
              </h1>
            </td>
          </tr>
          <tr>
            <td style="padding: 32px;">
              <h2 style="margin: 0 0 12px; font-size: 18px; font-weight: 700; color: #0F172A;">
                Your password was updated
              </h2>
              <p style="margin: 0 0 16px; font-size: 14px; color: #475569; line-height: 1.6;">
                Hello <strong>{user_name}</strong>,
              </p>
              <p style="margin: 0 0 16px; font-size: 14px; color: #475569; line-height: 1.6;">
                Your account password has been successfully updated. You can now log in using your new credentials.
              </p>
              <p style="margin: 0 0 16px; font-size: 13px; color: #DC2626; line-height: 1.5; font-weight: 600;">
                If you did not initiate this change, please contact Airsine Support immediately to secure your medical account.
              </p>
            </td>
          </tr>
          <tr>
            <td style="background-color: #F8FAFC; border-top: 1px solid #E2E8F0; padding: 18px; text-align: center;">
              <p style="margin: 0; font-size: 12px; color: #94A3B8;">&copy; Airsine Healthcare. All rights reserved.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    @classmethod
    def send_password_reset_email(
        cls,
        to_email: str,
        user_name: str,
        otp: str,
        reset_token: Optional[str] = None
    ) -> bool:
        """
        Send the password reset OTP email.
        If SMTP credentials are not configured, prints a clear development banner.
        """
        subject = f"Password Reset Code: {otp} - Airsine Healthcare"
        expire_minutes = getattr(settings, "OTP_EXPIRE_MINUTES", 10)
        html_content = cls._create_reset_email_html(user_name, otp, expire_minutes)
        text_content = (
            f"Hello {user_name},\n\n"
            f"Your Airsine Healthcare password reset verification code is: {otp}\n\n"
            f"This code will expire in {expire_minutes} minutes.\n"
            f"If you did not request this reset, please ignore this email.\n\n"
            f"- Airsine Healthcare Team"
        )

        return cls._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            dev_context={"OTP": otp, "ResetToken": reset_token, "User": user_name}
        )

    @classmethod
    def send_password_changed_notification(cls, to_email: str, user_name: str) -> bool:
        """Send notification that the password was updated."""
        subject = "Security Alert: Password Changed - Airsine Healthcare"
        html_content = cls._create_password_changed_html(user_name)
        text_content = (
            f"Hello {user_name},\n\n"
            f"Your Airsine account password was changed successfully.\n"
            f"If you did not make this change, please contact support immediately.\n\n"
            f"- Airsine Healthcare Team"
        )
        return cls._send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            dev_context={"Notice": "Password changed successfully", "User": user_name}
        )

    @staticmethod
    def _get_ssl_context():
        """Create a robust SSL context with fallback for local CA certificates."""
        try:
            import certifi
            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            try:
                return ssl.create_default_context()
            except Exception:
                return ssl._create_unverified_context()

    @classmethod
    def _send_email(
        cls,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        dev_context: Optional[dict] = None
    ) -> bool:
        """
        Deliver email using SMTP with dynamic env reloading and automatic
        fallback between Port 587 (STARTTLS) and Port 465 (SSL).
        """
        # Ensure fresh environment configuration is loaded
        try:
            reload_environment()
        except Exception:
            pass

        smtp_user = (os.getenv("SMTP_USER") or getattr(settings, "SMTP_USER", "") or "").strip()
        smtp_password = (os.getenv("SMTP_PASSWORD") or getattr(settings, "SMTP_PASSWORD", "") or "").replace(" ", "").strip()
        smtp_server = (os.getenv("SMTP_SERVER") or getattr(settings, "SMTP_SERVER", "smtp.gmail.com") or "smtp.gmail.com").strip()
        
        try:
            configured_port = int(os.getenv("SMTP_PORT") or getattr(settings, "SMTP_PORT", 587))
        except (ValueError, TypeError):
            configured_port = 587

        # If SMTP is not configured, print friendly dev banner and return True
        if not smtp_user or not smtp_password:
            print(f"\n[EMAIL NOTICE] No SMTP credentials configured. Printing OTP to console.")
            cls._print_dev_email_banner(to_email, subject, dev_context)
            return True

        from_email = (os.getenv("SMTP_FROM_EMAIL") or getattr(settings, "SMTP_FROM_EMAIL", "") or smtp_user).strip()
        from_name = os.getenv("SMTP_FROM_NAME") or getattr(settings, "SMTP_FROM_NAME", "Airsine Healthcare")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = to_email

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        msg_str = msg.as_string()

        # Decide port order: configured port first, alternative port second
        ports_to_try = [configured_port]
        alt_port = 465 if configured_port == 587 else 587
        if alt_port not in ports_to_try:
            ports_to_try.append(alt_port)

        delivery_error = None

        for port in ports_to_try:
            try:
                print(f"[EMAIL SERVICE] Attempting SMTP delivery to {to_email} via {smtp_server}:{port}...")

                if port == 465:
                    # SSL Mode
                    context = cls._get_ssl_context()
                    with smtplib.SMTP_SSL(smtp_server, port, context=context, timeout=15) as server:
                        server.ehlo()
                        server.login(smtp_user, smtp_password)
                        server.sendmail(from_email, [to_email], msg_str)
                else:
                    # STARTTLS Mode (587)
                    context = cls._get_ssl_context()
                    with smtplib.SMTP(smtp_server, port, timeout=15) as server:
                        server.ehlo()
                        try:
                            server.starttls(context=context)
                        except ssl.SSLError:
                            server.starttls(context=ssl._create_unverified_context())
                        server.ehlo()
                        server.login(smtp_user, smtp_password)
                        server.sendmail(from_email, [to_email], msg_str)

                print(f"[EMAIL SERVICE] SUCCESS: Real email successfully delivered to {to_email} via port {port}!\n")
                logger.info(f"Password reset email dispatched to {to_email} via port {port}")
                return True

            except Exception as e:
                delivery_error = e
                print(f"[EMAIL SERVICE] Warning: Port {port} delivery failed: {str(e)}")
                continue

        # If both attempts failed:
        logger.error(f"Failed to send email via SMTP to {to_email}: {str(delivery_error)}")
        cls._print_dev_email_banner(to_email, subject, dev_context, error=str(delivery_error))
        return False

    @staticmethod
    def _print_dev_email_banner(
        to_email: str,
        subject: str,
        dev_context: Optional[dict] = None,
        error: Optional[str] = None
    ):
        """Print an eye-catching terminal banner for development/testing."""
        border = "=" * 70
        print("\n" + border)
        if error:
            print(f" [EMAIL NOTICE - SMTP ERROR FALLBACK]")
            print(f" Reason: {error}")
        else:
            print(f" [EMAIL SERVICE - DEVELOPMENT MODE]")
        print(border)
        print(f" To:       {to_email}")
        print(f" Subject:  {subject}")
        if dev_context:
            for k, v in dev_context.items():
                if v:
                    print(f" {k:<10}: {v}")
        print(border)
        print(" (Set SMTP_USER and SMTP_PASSWORD in .env to send real emails via SMTP)")
        print(border + "\n")
