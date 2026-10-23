"""Runtime configuration read from environment variables.

Variable names are fixed by ``docs/CONTEXT.md`` section 6: ``DATABASE_URL``,
``APP_ENV``, ``CORS_ALLOWED_ORIGINS``. Nothing is read from files and no secret
has a default here.
"""

import os
from dataclasses import dataclass

DEFAULT_CORS_ORIGINS = ("http://localhost:5173", "http://127.0.0.1:5173")


@dataclass(frozen=True)
class Settings:
    """Validated runtime settings."""

    app_env: str
    cors_allowed_origins: tuple[str, ...]
    database_url: str | None


def _split_origins(raw: str | None) -> tuple[str, ...]:
    if raw is None or not raw.strip():
        return DEFAULT_CORS_ORIGINS
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    """Build settings from the process environment (injectable for tests)."""

    source = os.environ if environ is None else environ
    return Settings(
        app_env=source.get("APP_ENV", "development"),
        cors_allowed_origins=_split_origins(source.get("CORS_ALLOWED_ORIGINS")),
        database_url=source.get("DATABASE_URL"),
    )
