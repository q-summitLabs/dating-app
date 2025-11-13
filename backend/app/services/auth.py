from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import (
    get_password_hash,
    validate_password_length,
    verify_password,
)
from app.models.user import AuthUser, User
from app.schemas.auth import SignUpRequest


class AuthService:
    """Service layer handling authentication-related persistence logic."""

    @staticmethod
    async def get_auth_user_by_email(db: AsyncSession, email: str) -> Optional[AuthUser]:
        result = await db.execute(
            select(AuthUser)
            .where(AuthUser.email == email)
            .options(selectinload(AuthUser.profile))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_auth_user_by_id(db: AsyncSession, auth_user_id: int) -> Optional[AuthUser]:
        result = await db.execute(
            select(AuthUser)
            .where(AuthUser.id == auth_user_id)
            .options(selectinload(AuthUser.profile))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user_with_auth(db: AsyncSession, data: SignUpRequest) -> AuthUser:
        existing_auth = await AuthService.get_auth_user_by_email(db, data.email)
        if existing_auth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered.",
            )

        profile = User(
            name=data.name,
            email=data.email,
            phone_number=data.phone_number,
            interests=data.interests,
            location=data.location,
            pictures=data.pictures,
            prompts=data.prompts,
        )

        try:
            password_hash = get_password_hash(data.password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        auth_user = AuthUser(
            email=data.email,
            password_hash=password_hash,
            profile=profile,
        )
        db.add(auth_user)
        try:
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create user with the provided details.",
            ) from exc

        await db.refresh(auth_user, attribute_names=["profile"])
        return auth_user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[AuthUser]:
        auth_user = await AuthService.get_auth_user_by_email(db, email)
        if not auth_user:
            return None
        try:
            validate_password_length(password)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        if not verify_password(password, auth_user.password_hash):
            return None
        if not auth_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive.",
            )

        auth_user.last_login = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(auth_user, attribute_names=["profile"])
        return auth_user


auth_service = AuthService()

