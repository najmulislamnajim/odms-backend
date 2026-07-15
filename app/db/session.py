from collections.abc import AsyncGenerator 

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Engine
engine = create_async_engine(
    settings.async_database_url, 
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
)

# Session 
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db()-> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session 