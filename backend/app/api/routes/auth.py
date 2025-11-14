from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.database import get_db
from app.schemas.auth import (
    AuthResponse,
    AuthTokens,
    LoginRequest,
    SignUpRequest,
    TokenRefreshRequest,
)
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(auth_user_id: UUID, *, user_id: UUID) -> AuthTokens:
    claims = {"user_id": str(user_id)}
    access = create_access_token(str(auth_user_id), additional_claims=claims)
    refresh = create_refresh_token(str(auth_user_id), additional_claims=claims)
    return AuthTokens(access_token=access, refresh_token=refresh)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: SignUpRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    auth_user = await auth_service.create_user_with_auth(db, payload)
    tokens = _issue_tokens(auth_user.id, user_id=auth_user.user_id)
    return AuthResponse(tokens=tokens, user=auth_user.profile)


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    auth_user = await auth_service.authenticate_user(db, payload.email, payload.password)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    tokens = _issue_tokens(auth_user.id, user_id=auth_user.user_id)
    return AuthResponse(tokens=tokens, user=auth_user.profile)


@router.post("/token/refresh", response_model=AuthTokens)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokens:
    try:
        data = decode_token(payload.refresh_token)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        ) from exc

    if data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provided token is not a refresh token.",
        )

    subject = data.get("sub")
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    try:
        auth_user_id = UUID(subject)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        ) from exc

    auth_user = await auth_service.get_auth_user_by_id(db, auth_user_id)
    if not auth_user or not auth_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive user.",
        )

    return _issue_tokens(auth_user.id, user_id=auth_user.user_id)

