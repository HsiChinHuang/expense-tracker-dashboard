"""Unit tests for the Settings object (t5, REQ-BE-010/011/012).

Class and function names are part of the issue contract: the AC
verification commands reference these exact pytest node IDs. Defaults
are asserted against the repository-root `.env.example` file itself so
the two can never silently drift.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config import Settings

ENV_EXAMPLE = Path(__file__).resolve().parents[3] / ".env.example"

APP_VARS = (
    "DATABASE_URL",
    "DB_CONNECT_TIMEOUT",
    "JWT_SECRET",
    "JWT_ALGORITHM",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    "JWT_ISSUER",
    "JWT_AUDIENCE",
    "CORS_ORIGINS",
    "ENVIRONMENT",
    "APP_VERSION",
)

INT_VARS = ("DB_CONNECT_TIMEOUT", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES")


def _env_example_values() -> dict[str, str]:
    """Parse the application variables out of the root `.env.example`.

    Returns:
        dict[str, str]: Mapping of each expected app variable to its raw
        documented value.

    Raises:
        KeyError: If an expected application variable is missing.
    """
    values: dict[str, str] = {}
    for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, raw = stripped.partition("=")
        values[key.strip()] = raw.strip()
    return {name: values[name] for name in APP_VARS}


class TestSettings:
    """Contract coverage for app.config.Settings."""

    def test_env_var_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An environment variable beats the documented default."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:////tmp/t5_override.db")
        monkeypatch.setenv("APP_VERSION", "9.9.9")

        settings = Settings()

        assert settings.DATABASE_URL == "sqlite:////tmp/t5_override.db"
        assert settings.APP_VERSION == "9.9.9"

    def test_defaults_match_env_example(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Every default equals the value documented in `.env.example`."""
        for name in APP_VARS:
            monkeypatch.delenv(name, raising=False)
        documented = _env_example_values()

        defaults = Settings()

        for name in APP_VARS:
            raw = documented[name]
            actual = getattr(defaults, name)
            if name == "CORS_ORIGINS":
                assert actual == ["http://localhost:5173"]
            elif name in INT_VARS:
                assert actual == int(raw)
            else:
                assert actual == raw

    def test_production_rejects_default_secret(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Production construction fails on empty/placeholder JWT_SECRET."""
        monkeypatch.setenv("ENVIRONMENT", "production")

        with pytest.raises(ValidationError):
            Settings(JWT_SECRET="change-me")
        with pytest.raises(ValidationError):
            Settings(JWT_SECRET="")

    def test_development_allows_default_secret(self) -> None:
        """Development tolerates the documented placeholder secret."""
        settings = Settings(ENVIRONMENT="development", JWT_SECRET="change-me")

        assert settings.JWT_SECRET == "change-me"
