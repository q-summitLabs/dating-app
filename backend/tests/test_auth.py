import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import AuthUser, User


def _build_signup_payload(email: str, password: str = "P@ssword123") -> dict:
    return {
        "email": email,
        "password": password,
        "name": "Demo User",
        "phone_number": "+15555550123",
        "interests": ["hiking", "music"],
        "location": "San Francisco",
        "pictures": ["https://example.com/photo1.jpg"],
        "prompts": {"bio": "Just testing!"},
    }


@pytest.mark.asyncio
async def test_signup_creates_user_and_returns_tokens(client: AsyncClient, db_session):
    email = "signup_tester@example.com"
    payload = _build_signup_payload(email)

    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["user"]["email"] == email
    assert data["tokens"]["access_token"]
    assert data["tokens"]["refresh_token"]

    user_in_db = (
        await db_session.execute(select(User).where(User.email == email))
    ).scalar_one()
    assert user_in_db.name == payload["name"]

    auth_user_in_db = (
        await db_session.execute(select(AuthUser).where(AuthUser.email == email))
    ).scalar_one()
    assert auth_user_in_db.user_id == user_in_db.id


@pytest.mark.asyncio
async def test_login_returns_tokens(client: AsyncClient):
    email = "login_tester@example.com"
    password = "LoginPass123!"
    signup_payload = _build_signup_payload(email, password)

    signup_response = await client.post("/auth/signup", json=signup_payload)
    assert signup_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert data["user"]["email"] == email
    assert data["tokens"]["access_token"]
    assert data["tokens"]["refresh_token"]


@pytest.mark.asyncio
async def test_signup_rejects_overlong_password(client: AsyncClient):
    email = "long_password@example.com"
    long_password = "A" * 80
    payload = _build_signup_payload(email, long_password)

    response = await client.post("/auth/signup", json=payload)
    assert response.status_code == 422

