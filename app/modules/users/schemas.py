from __future__ import annotations

from datetime import datetime
from math import ceil
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBaseInput(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr
    nama: Optional[str] = None
    telepon: str = Field(default="")
    alamat: str = Field(default="")
    is_active: int = Field(default=1, ge=0, le=1)
    is_verified: int = Field(default=0, ge=0, le=1)
    is_admin: int = Field(default=0, ge=0, le=1)


class UserCreate(UserBaseInput):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    nama: Optional[str] = None
    telepon: Optional[str] = None
    alamat: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    is_active: Optional[int] = Field(default=None, ge=0, le=1)
    is_verified: Optional[int] = Field(default=None, ge=0, le=1)
    is_admin: Optional[int] = Field(default=None, ge=0, le=1)


class UserRead(BaseModel):
    id: str
    username: str
    email: EmailStr
    nama: Optional[str]
    telepon: str
    alamat: str
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, *, total: int, page: int, limit: int) -> "Pagination":
        pages = ceil(total / limit) if total else 0
        has_next = page < pages if pages else False
        has_prev = page > 1
        return cls(
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=has_next,
            has_prev=has_prev,
        )


class Meta(BaseModel):
    pagination: Pagination


class BaseResponse(BaseModel):
    status: str = "success"
    message: str


class UserResponse(BaseResponse):
    data: UserRead


class UsersResponse(BaseResponse):
    data: List[UserRead]
    meta: Meta


class MessageResponse(BaseResponse):
    data: Optional[dict] = None
