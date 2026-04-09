"""Authentication routes."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.security import get_current_user
from app.api.schemas.auth import LoginRequest, LoginResponse, UserOut
from app.application.auth import AuthService, InvalidCredentialsError
from app.config import Settings, get_settings
from app.domain.entities import User
from app.infrastructure.database import get_db
from app.infrastructure.users import SqlAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[Session, Depends(get_db)]


def get_auth_service(db: SessionDep, settings: SettingsDep) -> AuthService:
    return AuthService(
        user_repository=SqlAlchemyUserRepository(db),
        jwt_secret=settings.jwt_secret,
        jwt_algorithm=settings.jwt_algorithm,
        token_expires_minutes=settings.jwt_expires_minutes,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    body: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> LoginResponse:
    try:
        result = auth_service.login(phone=body.phone, password=body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный номер телефона или пароль",
        )

    return LoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        user=UserOut(
            id=result.user.id,
            name=result.user.name,
            phone=result.user.phone,
            role=result.user.role,
        ),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        phone=current_user.phone,
        role=current_user.role,
    )
