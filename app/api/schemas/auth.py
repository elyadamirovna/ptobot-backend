"""Pydantic schemas for auth endpoints."""
from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    phone: str = Field(..., examples=["+7 (900) 000-00-01"])
    password: str = Field(..., min_length=1)


class UserOut(BaseModel):
    id: str
    name: str
    phone: str
    role: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
