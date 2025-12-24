from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.database import get_db
from app.schemas.auth import (
    AuthResponse,
    AuthTokens,
    LoginRequest,
    SignUpRequest,
    TokenRefreshRequest,
)
from app.schemas.user import UserRead
from app.services.auth import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/test-code-version")
async def test_code_version():
    """Test endpoint to verify server has latest code."""
    from app.services.auth import auth_service
    import inspect
    sig = inspect.signature(auth_service.get_auth_user_by_id)
    param_type = sig.parameters['auth_user_id'].annotation
    return {
        "status": "ok",
        "auth_user_id_type": str(param_type),
        "code_version": "updated"
    }


def _issue_tokens(auth_user_id: int, *, user_id: UUID) -> AuthTokens:
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
    try:
        auth_user = await auth_service.authenticate_user(db, payload.email, payload.password)
        if not auth_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )
        
        if not auth_user.profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User profile not found.",
            )
        
        tokens = _issue_tokens(auth_user.id, user_id=auth_user.user_id)
        
        # Create response - Pydantic will handle conversion from SQLAlchemy model
        try:
            return AuthResponse(tokens=tokens, user=auth_user.profile)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create response: {type(e).__name__}: {str(e)}",
            ) from e
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"{type(e).__name__}: {str(e)}"
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {error_detail}",
        ) from e


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
        auth_user_id = int(subject)
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

