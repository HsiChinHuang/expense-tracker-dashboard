"""Application settings loaded from environment variables and .env.

Priority per REQ-ARCH-061: environment variable > `.env` file > default.
The defaults mirror the 13 application variables documented in the
repository-root `.env.example` (requirements/Chapter3_TechStack.md §3.10).
Frontend/MCP variables (VITE_API_BASE_URL, MCP_API_BASE_URL,
MCP_JWT_SECRET) are deliberately out of backend scope.
"""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PLACEHOLDER_JWT_SECRET = "change-me"
"""Documented placeholder secret from `.env.example` (never a real key)."""


class Settings(BaseSettings):
    """Backend configuration (REQ-BE-010).

    Fields are populated from environment variables first, then the
    optional `backend/.env` file, then the defaults below — which are
    exactly the values merged into `.env.example` by t4.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./dev.db"
    DB_CONNECT_TIMEOUT: int = 5
    JWT_SECRET: str = PLACEHOLDER_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_ISSUER: str = "expense-tracker"
    JWT_AUDIENCE: str = "expense-tracker-api"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    ENVIRONMENT: Literal["development", "production"] = "development"
    APP_VERSION: str = "1.0.0"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Allow a comma-separated CORS_ORIGINS value in addition to JSON.

        Args:
            value: Raw configuration value for CORS_ORIGINS.

        Returns:
            object: The value unchanged when it is JSON or a list; a split
            list when it is a plain comma-separated string.
        """
        if isinstance(value, str) and not value.strip().startswith("["):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @model_validator(mode="after")
    def _reject_weak_secret_in_production(self) -> "Settings":
        """Refuse empty or placeholder JWT secrets in production (REQ-BE-012).

        Returns:
            Settings: The validated settings instance.

        Raises:
            ValueError: When ENVIRONMENT is "production" and JWT_SECRET is
                empty or the documented placeholder.
        """
        if self.ENVIRONMENT == "production" and self.JWT_SECRET in ("", PLACEHOLDER_JWT_SECRET):
            msg = "JWT_SECRET must be set to a real secret in production"
            raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance (REQ-BE-011).

    Returns:
        Settings: The settings object, constructed once per process.
    """
    return Settings()
