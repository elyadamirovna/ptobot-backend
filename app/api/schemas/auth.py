"""Pydantic schemas for auth endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    phone: str = Field(..., examples=["+7 (900) 000-00-01"])
    password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    id: str
    name: str
    company_name: str | None = None
    phone: str
    role: str
    is_active: bool = True


class ContractorOption(BaseModel):
    id: str
    name: str
    company_name: str | None = None
    phone: str
    is_active: bool = True


class PtoEngineerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=5, max_length=32)
    password: str = Field(..., min_length=6, max_length=128)
    company_name: str | None = Field(default=None, max_length=255)


class ContractorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=5, max_length=32)
    password: str = Field(..., min_length=6, max_length=128)
    company_name: str | None = Field(default=None, max_length=255)


class AdminUserUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=5, max_length=32)
    company_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=6, max_length=128)
    is_active: bool = True


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
