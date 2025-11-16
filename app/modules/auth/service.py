from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.modules.auth.schemas import AuthTokenData, LoginRequest, UserInfo
from app.modules.users.repository import get_by_username


def _resolve_timezone() -> timezone:
    try:
        return ZoneInfo(settings.timezone)
    except ZoneInfoNotFoundError:
        offset_hours = 7 if settings.timezone == "Asia/Jakarta" else 0
        return timezone(timedelta(hours=offset_hours))


jakarta_tz = _resolve_timezone()


async def authenticate_and_issue_token(session: AsyncSession, payload: LoginRequest) -> AuthTokenData:
    """Validate credentials and create a JWT payload for successful authentication."""

    user = await get_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nama pengguna atau kata sandi tidak valid",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun belum aktif",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Akun belum terverifikasi",
        )

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    expires_at = datetime.now(tz=jakarta_tz) + expires_delta
    token = create_access_token(
        {
            "sub": user.id,
            "email": user.email,
            "role": str(getattr(user, "role", "user")),
        },
        expires_delta=expires_delta,
    )

    return AuthTokenData(
        access_token=token,
        expires_at=expires_at,
        user=UserInfo.model_validate(user),
    )
