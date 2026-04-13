"""Authentication routes."""
from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.security import get_current_user
from app.api.schemas.auth import AdminUserUpdate, ContractorCreate, ContractorOption, LoginRequest, LoginResponse, PtoEngineerCreate, UserOut
from app.application.auth import AuthService, InvalidCredentialsError, normalize_phone
from app.application.auth.security import hash_password
from app.config import Settings, get_settings
from app.domain.ports import UserRepository
from app.domain.entities import User
from app.infrastructure.database import get_db
from app.infrastructure.reports.models import ReportModel
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
            is_active=result.user.is_active,
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
        is_active=current_user.is_active,
    )


def get_user_repository(db: SessionDep) -> UserRepository:
    return SqlAlchemyUserRepository(db)


def _ensure_admin(current_user: User) -> None:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступно только администратору",
        )


def _update_user(
    *,
    repository: UserRepository,
    user_id: str,
    role: str,
    body: AdminUserUpdate,
) -> User:
    existing = repository.get_by_id(user_id)
    if existing is None or existing.role != role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    normalized_phone = normalize_phone(body.phone)
    phone_owner = repository.get_by_phone(normalized_phone)
    if phone_owner is not None and phone_owner.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким телефоном уже существует",
        )

    updated = repository.update(
        User(
            id=existing.id,
            name=body.name.strip(),
            company_name=body.company_name.strip() if body.company_name else None,
            phone=normalized_phone,
            hashed_password=hash_password(body.password) if body.password else existing.hashed_password,
            role=existing.role,
            is_active=body.is_active,
        )
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return updated


@router.get("/contractors", response_model=list[ContractorOption])
def list_contractors(
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[ContractorOption]:
    _ensure_admin(current_user)

    return [
        ContractorOption(
            id=user.id,
            name=user.name,
            company_name=user.company_name,
            phone=user.phone,
            is_active=user.is_active,
        )
        for user in repository.list_all_by_role("contractor")
    ]


@router.post("/contractors", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_contractor(
    body: ContractorCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    _ensure_admin(current_user)

    normalized_phone = normalize_phone(body.phone)
    existing = repository.get_by_phone(normalized_phone)
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
            phone=normalized_phone,
            hashed_password=hash_password(body.password),
            role="contractor",
            is_active=True,
        )
    )

    return UserOut(
        id=user.id,
        name=user.name,
        company_name=user.company_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )


@router.patch("/contractors/{user_id}", response_model=UserOut)
def update_contractor(
    user_id: str,
    body: AdminUserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    _ensure_admin(current_user)
    user = _update_user(repository=repository, user_id=user_id, role="contractor", body=body)
    return UserOut(
        id=user.id,
        name=user.name,
        company_name=user.company_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )


@router.delete("/contractors/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contractor(
    user_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    db: SessionDep,
) -> Response:
    _ensure_admin(current_user)
    existing = repository.get_by_id(user_id)
    if existing is None or existing.role != "contractor":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подрядчик не найден",
        )

    report_exists = db.execute(
        select(ReportModel.id).where(ReportModel.user_id == user_id).limit(1)
    ).scalar_one_or_none()
    if report_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Нельзя удалить подрядчика, пока за ним закреплены отчёты",
        )

    deleted = repository.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подрядчик не найден",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/pto-engineers", response_model=list[UserOut])
def list_pto_engineers(
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> list[UserOut]:
    _ensure_admin(current_user)

    return [
        UserOut(
            id=user.id,
            name=user.name,
            company_name=user.company_name,
            phone=user.phone,
            role=user.role,
            is_active=user.is_active,
        )
        for user in repository.list_all_by_role("pto_engineer")
    ]


@router.post("/pto-engineers", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_pto_engineer(
    body: PtoEngineerCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    _ensure_admin(current_user)

    normalized_phone = normalize_phone(body.phone)
    existing = repository.get_by_phone(normalized_phone)
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
            phone=normalized_phone,
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
        is_active=user.is_active,
    )


@router.patch("/pto-engineers/{user_id}", response_model=UserOut)
def update_pto_engineer(
    user_id: str,
    body: AdminUserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    _ensure_admin(current_user)
    user = _update_user(repository=repository, user_id=user_id, role="pto_engineer", body=body)
    return UserOut(
        id=user.id,
        name=user.name,
        company_name=user.company_name,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
    )
