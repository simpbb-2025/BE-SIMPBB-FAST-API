from __future__ import annotations

from fastapi import APIRouter

from app.core.deps import CurrentUserDep, SessionDep
from app.modules.auth import service as auth_service
from app.modules.auth.schemas import LoginRequest, LoginResponse, ProfileResponse, UserInfo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=200)
async def login(payload: LoginRequest, session: SessionDep) -> LoginResponse:
    token_data = await auth_service.authenticate_and_issue_token(session, payload)
    return LoginResponse(message="Login berhasil", data=token_data)


@router.get("/me", response_model=ProfileResponse)
async def read_profile(current_user: CurrentUserDep) -> ProfileResponse:
    user_data = UserInfo.model_validate(current_user)
    return ProfileResponse(message="Profil pengguna", data=user_data)
