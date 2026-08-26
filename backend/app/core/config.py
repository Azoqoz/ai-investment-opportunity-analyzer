"""Minimal environment-based FastAPI configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


DEFAULT_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def _parse_allowed_origins(value: str | None) -> tuple[str, ...]:
    configured = [] if value is None else value.split(",")
    origins = [*DEFAULT_ALLOWED_ORIGINS, *(item.strip() for item in configured)]
    unique_origins = tuple(dict.fromkeys(item for item in origins if item))
    if "*" in unique_origins:
        raise ValueError("ALLOWED_ORIGINS must contain explicit origins, not '*'")
    return unique_origins


@dataclass(frozen=True)
class Settings:
    """Runtime settings read from environment variables."""

    allowed_origins: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            allowed_origins=_parse_allowed_origins(
                os.getenv("ALLOWED_ORIGINS")
            )
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return process-wide application settings."""
    return Settings.from_environment()
