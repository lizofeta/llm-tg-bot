from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from app.core.config import get_db_url, get_settings

# настройки
settings = get_settings()
DB_URL = get_db_url(settings)

# engine
engine = create_async_engine(
    DB_URL,
    echo = settings.env == "local"
)

# фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False 
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
