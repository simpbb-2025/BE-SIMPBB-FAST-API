from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.modules.auth.schemas import TokenPayload
from app.modules.users.repository import get_by_id
from app.modules.users.models import User

bearer_scheme = HTTPBearer(auto_error=True)


async def get_async_session(session: AsyncSession = Depends(get_db)) -> AsyncSession:
    return session


SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Validate the bearer token and return the associated user."""

    token = credentials.credentials
    unauthorized_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload_data = decode_access_token(token)
        payload = TokenPayload.model_validate(payload_data)
    except (PyJWTError, ValueError):
        raise unauthorized_error

    if payload.sub is None:
        raise unauthorized_error

    user = await get_by_id(session, str(payload.sub))
    if user is None or not user.is_active or not user.is_verified:
        raise unauthorized_error

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
