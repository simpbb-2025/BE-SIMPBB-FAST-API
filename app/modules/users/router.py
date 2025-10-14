from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.modules.users import schemas, service
from app.modules.users.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: schemas.UserCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.UserResponse:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user = await service.create_user(session, payload)
    data = schemas.UserRead.model_validate(user)
    return schemas.UserResponse(message="User created successfully", data=data)


@router.get("/profile/me", response_model=schemas.UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)) -> schemas.UserResponse:
    data = schemas.UserRead.model_validate(current_user)
    return schemas.UserResponse(message="Profile retrieved successfully", data=data)


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def read_user_by_id(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.UserResponse:
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user = await service.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    data = schemas.UserRead.model_validate(user)
    return schemas.UserResponse(message="User detail retrieved successfully", data=data)


@router.get("/", response_model=schemas.UsersResponse)
async def list_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.UsersResponse:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    offset = (page - 1) * limit
    users, total = await service.list_users(session, offset=offset, limit=limit)
    data = [schemas.UserRead.model_validate(user) for user in users]
    pagination = schemas.Pagination.create(total=total, page=page, limit=limit)
    meta = schemas.Meta(pagination=pagination)
    return schemas.UsersResponse(message="Data users retrieved successfully", data=data, meta=meta)


@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user_by_id(
    user_id: str,
    payload: schemas.UserUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.UserResponse:
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user = await service.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated = await service.update_user(session, user, payload)
    data = schemas.UserRead.model_validate(updated)
    return schemas.UserResponse(message="User updated successfully", data=data)


@router.patch("/profile/me", response_model=schemas.UserResponse)
async def update_current_user(
    payload: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> schemas.UserResponse:
    updated = await service.update_user(session, current_user, payload)
    data = schemas.UserRead.model_validate(updated)
    return schemas.UserResponse(message="Profile updated successfully", data=data)


@router.delete("/{user_id}", response_model=schemas.MessageResponse)
async def delete_user_by_id(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.MessageResponse:
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    user = await service.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await service.delete_user(session, user)
    return schemas.MessageResponse(message="Deleted successfully")
