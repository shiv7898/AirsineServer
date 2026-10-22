import os
from dotenv import load_dotenv

def reload_environment():
    """Reload environment files dynamically."""
    load_dotenv(".env", override=True)
    env = os.getenv("APP_ENV", "dev").lower()
    if env == "prod" and os.path.exists(".env.prod"):
        load_dotenv(".env.prod", override=True)
    elif env == "dev" and os.path.exists(".env.dev"):
        load_dotenv(".env.dev", override=True)

reload_environment()


class Settings:
    @property
    def APP_ENV(self) -> str:
        return os.getenv("APP_ENV", "dev")

    @property
    def DATABASE_URL(self) -> str:
        return os.getenv("DATABASE_URL", "postgresql://postgres:AIR987@127.0.0.1:5432/hospitaldb")

    @property
    def SECRET_KEY(self) -> str:
        return os.getenv("SECRET_KEY", "hospital123")

    @property
    def ALGORITHM(self) -> str:
        return os.getenv("ALGORITHM", "HS256")

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

    @property
    def HOST(self) -> str:
        return os.getenv("HOST", "0.0.0.0")

    @property
    def PORT(self) -> int:
        return int(os.getenv("PORT", 8000))

    # SMTP / Email Configuration (dynamically retrieved)
    @property
    def SMTP_SERVER(self) -> str:
        return os.getenv("SMTP_SERVER", "smtp.gmail.com")

    @property
    def SMTP_PORT(self) -> int:
        return int(os.getenv("SMTP_PORT", 587))

    @property
    def SMTP_USER(self) -> str:
        return os.getenv("SMTP_USER", "").strip()

    @property
    def SMTP_PASSWORD(self) -> str:
        return os.getenv("SMTP_PASSWORD", "").strip()

    @property
    def SMTP_FROM_EMAIL(self) -> str:
        return os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER", "noreply@airsine.in"))

    @property
    def SMTP_FROM_NAME(self) -> str:
        return os.getenv("SMTP_FROM_NAME", "Airsine Healthcare")

    @property
    def SMTP_TLS(self) -> bool:
        return os.getenv("SMTP_TLS", "true").lower() in ("true", "1", "yes")

    @property
    def OTP_EXPIRE_MINUTES(self) -> int:
        return int(os.getenv("OTP_EXPIRE_MINUTES", 10))


settings = Settings()
