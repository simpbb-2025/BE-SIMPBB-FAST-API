from __future__ import annotations

from typing import Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.modules.users import repository, schemas
from app.modules.users.models import User


def _flag_to_bool(value: int | None, *, default: bool) -> bool:
    return bool(value) if value is not None else default


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
        is_admin=_flag_to_bool(payload.is_admin, default=False),
    )
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, payload: schemas.UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)

    if "password" in data and data["password"] is not None:
        data["hashed_password"] = get_password_hash(data.pop("password"))

    data.pop("password", None)

    for flag in ("is_active", "is_verified", "is_admin"):
        if flag in data and data[flag] is not None:
            data[flag] = bool(data[flag])

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
