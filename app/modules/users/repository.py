from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User


async def get_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
    normalized_email = email.strip().lower()
    result = await session.execute(
        select(User).where(func.lower(User.email) == normalized_email)
    )
    return result.scalar_one_or_none()


async def get_by_username(session: AsyncSession, username: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def list_users(session: AsyncSession, *, offset: int, limit: int) -> list[User]:
    stmt = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def count_users(session: AsyncSession) -> int:
    result = await session.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def create(
    session: AsyncSession,
    *,
    username: str,
    email: str,
    nama: str | None,
    telepon: str,
    alamat: str,
    hashed_password: str,
    is_active: bool,
    is_verified: bool,
    role: str,
    verification_code: str | None = None,
    verification_code_expires_at: datetime | None = None,
) -> User:
    now = datetime.utcnow()
    user = User(
        id=uuid4().hex,
        username=username,
        email=email,
        nama=nama,
        telepon=telepon,
        alamat=alamat,
        hashed_password=hashed_password,
        is_active=is_active,
        is_verified=is_verified,
        role=role,
        verification_code=verification_code,
        verification_code_expires_at=verification_code_expires_at,
        created_at=now,
        updated_at=now,
    )
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def update(session: AsyncSession, user: User, **kwargs) -> User:
    for key, value in kwargs.items():
        setattr(user, key, value)
    user.updated_at = datetime.utcnow()
    await session.flush()
    await session.refresh(user)
    return user


async def delete(session: AsyncSession, user: User) -> None:
    await session.delete(user)
