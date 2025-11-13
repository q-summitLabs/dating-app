import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.database import get_db
from app.main import app
from app.models.user import Base

@pytest.fixture(scope="session")
def test_database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set; skipping integration tests.")

    url_obj = make_url(url)
    if url_obj.drivername.startswith("postgresql") and not url_obj.drivername.endswith("+asyncpg"):
        url_obj = url_obj.set(drivername="postgresql+asyncpg")
    return url_obj.render_as_string(hide_password=False)


@pytest_asyncio.fixture
async def async_engine(test_database_url: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(test_database_url, future=True)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS yolk_staging"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("TRUNCATE TABLE yolk_staging.auth_users RESTART IDENTITY CASCADE"))
        await conn.execute(text("TRUNCATE TABLE yolk_staging.users RESTART IDENTITY CASCADE"))
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with async_engine.connect() as connection:
        session = AsyncSession(bind=connection, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await connection.execute(text("TRUNCATE TABLE yolk_staging.auth_users RESTART IDENTITY CASCADE"))
            await connection.execute(text("TRUNCATE TABLE yolk_staging.users RESTART IDENTITY CASCADE"))
            await connection.commit()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver") as test_client:
        yield test_client

    app.dependency_overrides.pop(get_db, None)

