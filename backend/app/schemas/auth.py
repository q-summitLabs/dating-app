from __future__ import annotations

from typing import Any, Dict, List, Optional, Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserRead


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=1)
    phone_number: Optional[str] = None
    interests: Optional[List[str]] = None
    location: Optional[str] = None
    pictures: Optional[List[str]] = None
    prompts: Optional[Dict[str, Any]] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class AuthResponse(BaseModel):
    tokens: AuthTokens
    user: UserRead


class TokenRefreshRequest(BaseModel):
    refresh_token: str

