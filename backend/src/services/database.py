from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from ..config import get_database_settings

metadata = MetaData()
Base = declarative_base(metadata=metadata)


async def get_engine() -> AsyncEngine:
    settings = get_database_settings()
    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
        f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    return create_async_engine(database_url, echo=True)


async def get_async_session_maker() -> async_sessionmaker:
    engine = await get_engine()
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = await get_async_session_maker()
    async with session_maker() as session:
        yield session
