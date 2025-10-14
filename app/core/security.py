from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from zoneinfo import ZoneInfo
from zoneinfo import ZoneInfoNotFoundError

import jwt
from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _resolve_timezone() -> timezone:
    try:
        return ZoneInfo(settings.timezone)
    except ZoneInfoNotFoundError:
        offset_hours = 7 if settings.timezone == "Asia/Jakarta" else 0
        return timezone(timedelta(hours=offset_hours))


jakarta_tz = _resolve_timezone()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if the provided password matches the stored hash."""

    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a bcrypt hash for the supplied password."""

    return password_context.hash(password)


def create_access_token(claims: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token for the given claims."""

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

    issued_at = datetime.now(tz=jakarta_tz)
    expire_at = issued_at + expires_delta

    payload = {
        **claims,
        "iat": int(issued_at.timestamp()),
        "exp": int(expire_at.timestamp()),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode an access token and return its payload."""

    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
