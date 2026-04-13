"""Authentication routes."""
from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.security import get_current_user
from app.api.schemas.auth import ContractorOption, LoginRequest, LoginResponse, PtoEngineerCreate, UserOut
from app.application.auth import AuthService, InvalidCredentialsError
from app.application.auth.security import hash_password
from app.config import Settings, get_settings
from app.domain.ports import UserRepository
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
            company_name=result.user.company_name,
            phone=result.user.phone,
            role=result.user.role,
        ),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return UserOut(
        id=current_user.id,
        name=current_user.name,
        company_name=current_user.company_name,
        phone=current_user.phone,
        role=current_user.role,
    )


def get_user_repository(db: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(db)


@router.get("/contractors", response_model=list[ContractorOption])
def list_contractors(
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[ContractorOption]:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только администратору",
        )

    return [
        ContractorOption(
            id=user.id,
            name=user.name,
            company_name=user.company_name,
            phone=user.phone,
        )
        for user in repository.list_contractors()
    ]


@router.get("/pto-engineers", response_model=list[UserOut])
def list_pto_engineers(
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[UserOut]:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только администратору",
        )

    return [
        UserOut(
            id=user.id,
            name=user.name,
            company_name=user.company_name,
            phone=user.phone,
            role=user.role,
        )
        for user in repository.list_by_role("pto_engineer")
    ]


@router.post("/pto-engineers", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_pto_engineer(
    body: PtoEngineerCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только администратору",
        )

    existing = repository.get_by_phone(body.phone.strip())
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким телефоном уже существует",
        )

    user = repository.add(
        User(
            id=uuid4().hex,
            name=body.name.strip(),
            company_name=body.company_name.strip() if body.company_name else None,
            phone=body.phone.strip(),
            hashed_password=hash_password(body.password),
            role="pto_engineer",
            is_active=True,
        )
    )

    return UserOut(
        id=user.id,
        name=user.name,
        company_name=user.company_name,
        phone=user.phone,
        role=user.role,
    )
