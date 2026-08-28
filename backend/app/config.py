"""
CloudGuard AI – Application Configuration
Loads all settings from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "CloudGuard AI"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ── Database ─────────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "cloudguard_db"

    # ── AI Provider ──────────────────────────────────────────────────────────
    AI_PROVIDER: str = "gemini"          # "gemini" | "openai"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # ── AWS ──────────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"

    # ── Alerts ───────────────────────────────────────────────────────────────
    ALERT_EMAIL_FROM: str = "alerts@cloudguard.ai"
    ALERT_EMAIL_TO: str = "admin@cloudguard.ai"
    SES_REGION: str = "us-east-1"

    # ── Reports ──────────────────────────────────────────────────────────────
    REPORTS_S3_BUCKET: str = "cloudguard-reports-bucket"

    # ── Demo Mode ────────────────────────────────────────────────────────────
    DEMO_MODE: bool = True

    @model_validator(mode="after")
    def validate_production_secret(self):
        if self.APP_ENV.lower() in {"prod", "production"}:
            weak_secrets = {
                "change-me-in-production",
                "your-super-secret-jwt-key-change-in-production",
            }
            if self.SECRET_KEY in weak_secrets or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY must be a strong value of at least 32 characters in production"
                )
        return self

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
