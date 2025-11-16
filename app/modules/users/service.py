from __future__ import annotations

from datetime import datetime, timedelta
import secrets
import string
from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import mailer
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.modules.users import repository, schemas
from app.modules.users.models import User


def _flag_to_bool(value: int | None, *, default: bool) -> bool:
    return bool(value) if value is not None else default


def _generate_verification_code(length: int) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


async def _send_and_store_verification_code(session: AsyncSession, user: User) -> None:
    code = _generate_verification_code(settings.registration_code_length).upper()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.registration_code_expire_minutes)
    await repository.update(
        session,
        user,
        verification_code=code,
        verification_code_expires_at=expires_at,
        is_active=False,
        is_verified=False,
    )

    try:
        await mailer.send_registration_code_email(user.email, code, expires_at)
    except Exception as exc:  # pragma: no cover - external dependency
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengirim kode verifikasi. Silakan coba lagi.",
        ) from exc


async def get_user_by_id(session: AsyncSession, user_id: str | None) -> Optional[User]:
    if not user_id:
        return None
    return await repository.get_by_id(session, user_id)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    return await repository.get_by_email(session, email)


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    return await repository.get_by_username(session, username)


async def list_users(session: AsyncSession, *, offset: int, limit: int) -> Tuple[list[User], int]:
    users = await repository.list_users(session, offset=offset, limit=limit)
    total = await repository.count_users(session)
    return users, total


async def create_user(session: AsyncSession, payload: schemas.UserCreate) -> User:
    existing_email = await repository.get_by_email(session, payload.email)
    if existing_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing_username = await repository.get_by_username(session, payload.username)
    if existing_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = get_password_hash(payload.password)
  
    role_value = payload.role.value if hasattr(payload.role, "value") else str(payload.role)
    if role_value not in {"admin", "staff"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'admin' or 'staff'")

    user = await repository.create(
        session,
        username=payload.username,
        email=payload.email,
        nama=payload.nama,
        telepon=payload.telepon or "",
        alamat=payload.alamat or "",
        hashed_password=hashed_password,
        is_active=_flag_to_bool(payload.is_active, default=True),
        is_verified=_flag_to_bool(payload.is_verified, default=False),
        role=role_value,
    )
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    session: AsyncSession,
    user: User,
    payload: schemas.UserUpdate,
    *,
    allow_admin_fields: bool = True,
) -> User:
    data = payload.model_dump(exclude_unset=True)

    if "password" in data and data["password"] is not None:
        data["hashed_password"] = get_password_hash(data.pop("password"))

    data.pop("password", None)

    if not allow_admin_fields:
        for flag in ("is_active", "is_verified", "role"):
            if flag in data:
                data.pop(flag)
    else:
        for flag in ("is_active", "is_verified"):
            if flag in data and data[flag] is not None:
                data[flag] = bool(data[flag])
        if "role" in data and data["role"] is not None:
            candidate = data["role"]
            if hasattr(candidate, "value"):
                data["role"] = candidate.value
            else:
                data["role"] = str(candidate)

    if data:
        await repository.update(session, user, **data)
        await session.commit()
        await session.refresh(user)

    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await repository.delete(session, user)
    await session.commit()


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    user = await repository.get_by_username(session, username)
    if user is None:
        return None
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def register_user(session: AsyncSession, payload: schemas.RegisterRequest) -> User:
    existing_email = await repository.get_by_email(session, payload.email)
    if existing_email is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing_username = await repository.get_by_username(session, payload.username)
    if existing_username is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = get_password_hash(payload.password)
    user = await repository.create(
        session,
        username=payload.username,
        email=payload.email,
        nama=payload.nama,
        telepon=payload.telepon or "",
        alamat=payload.alamat or "",
        hashed_password=hashed_password,
        is_active=False,
        is_verified=False,
        role="user",
    )
    await _send_and_store_verification_code(session, user)
    await session.commit()
    await session.refresh(user)
    return user


async def verify_registration_code(
    session: AsyncSession, payload: schemas.VerificationCodeVerifyRequest
) -> User:
    user = await repository.get_by_email(session, payload.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_verified:
        return user

    if not user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi belum dibuat untuk email ini",
        )

    if user.verification_code_expires_at and user.verification_code_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi sudah kedaluwarsa",
        )

    submitted_code = payload.verification_code.strip().upper()
    if submitted_code != user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kode verifikasi tidak valid",
        )

    updated = await repository.update(
        session,
        user,
        is_active=True,
        is_verified=True,
        verification_code=None,
        verification_code_expires_at=None,
    )
    await session.commit()
    await session.refresh(updated)
    return updated
