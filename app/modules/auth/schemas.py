from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    is_admin: bool


class TokenPayload(BaseModel):
    sub: str | None = None
    email: EmailStr | None = None
    is_admin: bool | None = None
    exp: int | None = None
    iat: int | None = None


class AuthTokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserInfo


class LoginResponse(BaseModel):
    success: bool = True
    message: str
    data: AuthTokenData


class ProfileResponse(BaseModel):
    success: bool = True
    message: str
    data: UserInfo
