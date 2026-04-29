import pytest

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import (
    async_sessionmaker, 
    create_async_engine, 
    AsyncSession
)

from collections.abc import AsyncGenerator

from app.db.base import Base

from fastapi import FastAPI
from app.api.deps import get_db
from app.core.config import get_settings
from app.api.router import api_router
from app.api.exception_handler import register_exception_handlers

# Fake settings for tests

class FakeSettings:
    jwt_secret = "test_secret"
    jwt_alg = "HS256"
    access_token_expire_minutes = 60

@pytest.fixture
def settings():
    return FakeSettings()

# In-memory SQLite 

DB_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(DB_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

@pytest.fixture(scope="function", autouse=True)
async def prepare_testing_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_testing_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


# test app

@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router)
    register_exception_handlers(app)

    app.dependency_overrides[get_db] = get_testing_db
    app.dependency_overrides[get_settings] = lambda: FakeSettings()

    return app


# client

@pytest.fixture
async def client(test_app: FastAPI):
    transport = ASGITransport(app=test_app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client
